# 7 e Mezzo 🎴

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)


<div align="center">
<table>
  <tr>
    <td align="center" width="40%">
      <img src="https://github.com/user-attachments/assets/1e4bbd9e-5b56-4d76-9e2e-53185f74941c" width="400"/>
      <br><br>
      <h1>7 e Mezzo</h1>
    </td>
    <td align="left" valign="top" width="60%">
      <i>
        <img align="left" src="https://github.com/user-attachments/assets/7bc2c8b4-3e66-47e2-aa2e-ee8325430ab4" width="100%" alt="Screenshot del gioco"/>
        <br><br>
        Abbiamo realizzato una fedelissima interpretazione del gioco di carte napoletano <strong>7 e mezzo</strong>.<br><br>
        Riteniamo sia molto utile per passare piacevoli serate con i propri amici, anche a distanza.<br><br>
        Questo gioco è molto simile al Black Jack francese, ma a renderlo speciale sono le sue figure napoletane, la loro storia e il modo unico di coinvolgere le persone.<br><br>
        La sua caratteristica principale è quella di:<br>
        • Consentire a più giocatori di giocare insieme contemporaneamente in tempo reale
      </i>
    </td>
  </tr>
</table>
</div>

<br><br>

## Screenshot
<img width="331" height="544" alt="Screenshot 2026-01-05 alle 20 38 15" src="https://github.com/user-attachments/assets/8eee5b0e-c8f4-4175-bb35-3b504b61d472" />
<img width="332" height="544" alt="Screenshot 2026-01-05 alle 20 39 09" src="https://github.com/user-attachments/assets/a1c1279e-f7fc-4607-a4c8-2034e4788510" />

<img width="320" height="545" alt="Screenshot 2026-01-05 alle 20 39 50" src="https://github.com/user-attachments/assets/30466692-217d-4089-95cc-4145fae442fd" />





## Descrizione

Un'implementazione web fedele del classico gioco napoletano **Sette e Mezzo**, giocabile online in multiplayer con amici a distanza. Usa un mazzo di carte napoletane e rispetta tutte le regole tradizionali, inclusa la "matta" (Re di Denari) e la possibilità di bruciare il 4.

## Features

- Multiplayer in tempo reale (più giocatori simultanei contro il banco)
- Interfaccia web semplice e responsive
- Regole tradizionali napoletane implementate fedelmente
- Giocabile da browser, anche su dispositivi diversi
- Server leggero e veloce grazie a FastAPI

## Tecnologie utilizzate

- **FastAPI** → backend e API
- **Uvicorn** → server ASGI
- **Jinja2** → templating HTML
- **python-multipart** → gestione input utente
- HTML/CSS/JavaScript per il frontend

## Installazione
Per installare il progetto basta semplicemente scaricare la cartella zippata e poi installare la venv con i seguenti comandi: 

python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload

## Regole del gioco 
le regole del gioco sono semplici, come in ogni gioco c'è un mazziere che distribuisce le carte, le prime carte dei giocatori saranno coperte mentre dalla seconda in poi le carte saranno scoperte, il giocatore che piu si avvicina a 7.50 vince invece chi supoera questo valore si dice che ha sballato. Se un giocatore ha pescato come prima carta un 4 puo decidere di bruciarlo e di sostituirlo con un altro carta mentre se esce il re di denari come prima carta ne puoi decidere il valore il quale ha un valore compreso tra 1-7.Bene detto le regole generali del gioco che spero che vi possiate divertire come noi l'abbiamo fatto realizzando questo gioco 😜.




  
