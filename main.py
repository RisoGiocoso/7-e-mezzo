from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Archivio globale dei giochi (in memoria, per semplicità)
games = {}

def create_deck():
    deck = []
    semi_map = {"b": "Bastoni", "c": "Coppe", "d": "Denari", "s": "Spade"}
    for s_abbr, s_name in semi_map.items():
        for v in range(1, 11):
            if v <= 7:
                punti = v
                nome = str(v)
            else:
                punti = 0.5
                if v == 8:
                    nome = "Fante"
                elif v == 9:
                    nome = "Cavallo"
                else:  # v == 10 Re
                    nome = "Re"
                    if s_abbr == "d":  # Re di Denari è speciale
                        punti = None  # valore flessibile 1-7
            img_path = f"/static/cards/{v}{s_abbr}.jpg"
            deck.append({
                "seme": s_name,
                "valore": v,
                "punti": punti,
                "nome": nome,
                "img": img_path,
                "is_re_denari": (v == 10 and s_abbr == "d")
            })
    random.shuffle(deck)
    return deck

def calculate_optimal_score(hand):
    base_score = 0.0
    re_denari_count = 0

    for card in hand:
        if card["is_re_denari"]:
            re_denari_count += 1
        elif card["punti"] is not None:
            base_score += card["punti"]

    if re_denari_count == 0:
        return base_score

    # Prova tutte le combinazioni di valori 1-7 per ogni Re di Denari
    best_score = 0.0
    for combo in range(7 ** re_denari_count):
        score = base_score
        temp = combo
        for _ in range(re_denari_count):
            val = (temp % 7) + 1  # 1 a 7
            score += val
            temp //= 7
        if score <= 7.5 and score > best_score:
            best_score = score

    # Se nessuna combinazione è <= 7.5, ritorna il minimo possibile (sballato comunque)
    if best_score == 0.0:
        best_score = base_score + re_denari_count * 1  # minimo con matta = 1

    return best_score

def get_current_player(game):
    for u in game["turn_order"]:
        if not game["players"][u]["stand"]:
            return u
    return None

def check_winner(game):
    valid_players = [(u, p["score"]) for u, p in game["players"].items() if p["score"] <= 7.5]
    if not valid_players:
        return "Banco"
    return max(valid_players, key=lambda x: x[1])[0]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "games": games})

@app.post("/create_game")
def create_game(username: str = Form(...)):
    game_id = str(len(games) + 1)
    games[game_id] = {
        "players": {
            username: {"hand": [], "score": 0.0, "stand": False, "burnable": False}
        },
        "deck": create_deck(),
        "turn_order": [username],
        "started": False,
        "finished": False,
        "winner": None,
        "pending_draw": None
    }
    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.post("/join")
def join(game_id: str = Form(...), username: str = Form(...)):
    game = games.get(game_id)
    if not game or game["started"] or username in game["players"]:
        return RedirectResponse("/", status_code=302)
    game["players"][username] = {"hand": [], "score": 0.0, "stand": False, "burnable": False}
    game["turn_order"].append(username)
    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.post("/start/{game_id}/{username}")
def start_game(game_id: str, username: str):
    game = games.get(game_id)
    if not game:
        return RedirectResponse("/", status_code=302)

    if username != game["turn_order"][0]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    if game["started"] and not game["finished"]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    game["started"] = True
    game["finished"] = False
    game["winner"] = None
    game["pending_draw"] = None

    for player in game["players"].values():
        player["hand"] = []
        player["score"] = 0.0
        player["stand"] = False
        player["burnable"] = False

    game["deck"] = create_deck()

    for player_name in game["turn_order"]:
        if game["deck"]:
            card = game["deck"].pop()
            player = game["players"][player_name]
            player["hand"].append(card)
            player["score"] = calculate_optimal_score(player["hand"])
            if card["valore"] == 4 and len(player["hand"]) == 1:
                player["burnable"] = True

    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.post("/draw/{game_id}/{username}")
def request_draw(game_id: str, username: str):
    game = games.get(game_id)
    if not game or not game["started"] or game["finished"]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    current_player = get_current_player(game)
    if username != current_player:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    dealer_name = game["turn_order"][0]
    player = game["players"][username]

    if username == dealer_name:
        if not game["deck"]:
            player["stand"] = True
        else:
            new_card = game["deck"].pop()
            player["hand"].append(new_card)
            player["score"] = calculate_optimal_score(player["hand"])
            if new_card["valore"] == 4 and len(player["hand"]) == 1:
                player["burnable"] = True

        if player["score"] > 7.5:
            player["stand"] = True
            player["burnable"] = False

        if all(p["stand"] for p in game["players"].values()):
            game["finished"] = True
            game["winner"] = check_winner(game)

    else:
        game["pending_draw"] = username

    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.post("/deal_card/{game_id}/{dealer_name}")
def deal_card(game_id: str, dealer_name: str):
    game = games.get(game_id)
    if not game or not game["started"] or game["finished"]:
        return RedirectResponse(f"/game/{game_id}/{dealer_name}", status_code=302)

    if dealer_name != game["turn_order"][0]:
        return RedirectResponse(f"/game/{game_id}/{dealer_name}", status_code=302)

    current_player_name = get_current_player(game)
    if not current_player_name or game["pending_draw"] != current_player_name:
        return RedirectResponse(f"/game/{game_id}/{dealer_name}", status_code=302)

    player = game["players"][current_player_name]
    game["pending_draw"] = None

    if not game["deck"]:
        player["stand"] = True
    else:
        new_card = game["deck"].pop()
        player["hand"].append(new_card)
        player["score"] = calculate_optimal_score(player["hand"])
        if new_card["valore"] == 4 and len(player["hand"]) == 1:
            player["burnable"] = True

    if player["score"] > 7.5:
        player["stand"] = True
        player["burnable"] = False

    if all(p["stand"] for p in game["players"].values()):
        game["finished"] = True
        game["winner"] = check_winner(game)

    return RedirectResponse(f"/game/{game_id}/{dealer_name}", status_code=302)

@app.post("/replace4/{game_id}/{username}")
def replace_four(game_id: str, username: str):
    game = games.get(game_id)
    if not game or not game["started"] or game["finished"]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    player = game["players"].get(username)
    if not player or username != get_current_player(game) or not player.get("burnable", False):
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    burned_card = None
    for i in reversed(range(len(player["hand"]))):
        if player["hand"][i]["valore"] == 4:
            burned_card = player["hand"].pop(i)
            break

    if not burned_card:
        player["burnable"] = False
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    player["burnable"] = False

    if not game["deck"]:
        player["stand"] = True
    else:
        new_card = game["deck"].pop()
        player["hand"].append(new_card)
        player["score"] = calculate_optimal_score(player["hand"])
        player["burnable"] = False

    if player["score"] > 7.5:
        player["stand"] = True
        player["burnable"] = False

    if all(p["stand"] for p in game["players"].values()):
        game["finished"] = True
        game["winner"] = check_winner(game)

    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.post("/stand/{game_id}/{username}")
def stand(game_id: str, username: str):
    game = games.get(game_id)
    if not game or not game["started"] or game["finished"]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    player = game["players"].get(username)
    if not player or player["stand"]:
        return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

    player["stand"] = True
    player["burnable"] = False

    if all(p["stand"] for p in game["players"].values()):
        game["finished"] = True
        game["winner"] = check_winner(game)

    return RedirectResponse(f"/game/{game_id}/{username}", status_code=302)

@app.get("/game/{game_id}/{username}", response_class=HTMLResponse)
def game_view(request: Request, game_id: str, username: str):
    game = games.get(game_id)
    if not game:
        return RedirectResponse("/", 302)
    
    current_player = None
    if game["started"] and not game["finished"]:
        current_player = get_current_player(game)
        if current_player is None:
            game["finished"] = True
            game["winner"] = check_winner(game)
    
    return templates.TemplateResponse("game.html", {
        "request": request,
        "game": game,
        "game_id": game_id,
        "username": username,
        "current_player": current_player
    })

@app.get("/status/{game_id}")
def game_status(game_id: str):
    game = games.get(game_id)
    if not game:
        return JSONResponse({"error": "game not found"})

    current_player = get_current_player(game) if game["started"] and not game["finished"] else None

    return JSONResponse({
        "players": {
            u: {
                "hand": p["hand"],
                "score": p["score"],
                "stand": p["stand"],
                "burnable": p.get("burnable", False)
            } for u, p in game["players"].items()
        },
        "started": game["started"],
        "finished": game["finished"],
        "winner": game["winner"],
        "current_player": current_player,
        "turn_order": game["turn_order"],
        "pending_draw": game.get("pending_draw")
    })

# === NUOVO ENDPOINT: ELIMINA PARTITA IN QUALSIASI MOMENTO ===
@app.post("/delete_game/{game_id}/{username}")
def delete_game_anytime(game_id: str, username: str):
    game = games.get(game_id)
    if not game:
        return RedirectResponse("/", status_code=302)
    
    if username not in game["players"]:
        return RedirectResponse("/", status_code=302)
    
    if game_id in games:
        del games[game_id]
    
    return RedirectResponse("/", status_code=302)

# Vecchio endpoint lasciato per compatibilità
@app.post("/delete_game/{game_id}/{creator_username}")
def delete_game_old(game_id: str, creator_username: str):
    return delete_game_anytime(game_id, creator_username)

@app.post("/leave/{game_id}/{username}")
def leave_game(game_id: str, username: str):
    game = games.get(game_id)
    if not game:
        return RedirectResponse("/", status_code=302)
    
    if username not in game["players"]:
        return RedirectResponse("/", status_code=302)
    
    del game["players"][username]
    if username in game["turn_order"]:
        game["turn_order"].remove(username)
    
    if len(game["players"]) == 0:
        if game_id in games:
            del games[game_id]
    
    return RedirectResponse("/", status_code=302)