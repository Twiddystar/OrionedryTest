from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return '''
    <html>
        <head><title>🩺 Dry Eye Questionnaire</title></head>
        <body>
            <h1>Benvenuto!</h1>
            <p>Vai al <a href='/questionario'>questionario</a> per determinare il tipo di occhio secco.</p>
        </body>
    </html>
    '''

@app.get("/questionario", response_class=HTMLResponse)
def questionario():
    return '''
    <html>
        <head><title>Questionario Occhio Secco</title></head>
        <body>
            <h2>Compila il questionario</h2>
            <form action="/risultato" method="post">
                <p>Hai bruciore o sensazione di corpo estraneo? <br>
                <input type="radio" name="bruciore" value="si"> Sì
                <input type="radio" name="bruciore" value="no"> No</p>

                <p>Ti lacrimano spesso gli occhi? <br>
                <input type="radio" name="lacrimazione" value="si"> Sì
                <input type="radio" name="lacrimazione" value="no"> No</p>

                <p>Senti dolore pungente o scosse anche senza stimoli? <br>
                <input type="radio" name="dolore" value="si"> Sì
                <input type="radio" name="dolore" value="no"> No</p>

                <p>Hai le palpebre arrossate o croste al margine? <br>
                <input type="radio" name="palpebre" value="si"> Sì
                <input type="radio" name="palpebre" value="no"> No</p>

                <input type="submit" value="Invia">
            </form>
        </body>
    </html>
    '''

@app.post("/risultato", response_class=HTMLResponse)
async def risultato(bruciore: str = Form(...), lacrimazione: str = Form(...), dolore: str = Form(...), palpebre: str = Form(...)):
    score = {
        "evaporativo": 0,
        "acquoso": 0,
        "neuropatico": 0
    }

    if bruciore == "si":
        score["evaporativo"] += 1
        score["acquoso"] += 1
    if lacrimazione == "si":
        score["acquoso"] += 2
    if dolore == "si":
        score["neuropatico"] += 2
    if palpebre == "si":
        score["evaporativo"] += 2

    tipo = max(score, key=score.get)

    tipo_full = {
        "evaporativo": "Occhio Secco Evaporativo",
        "acquoso": "Occhio Secco da Deficit Acquoso",
        "neuropatico": "Occhio Secco di tipo Neuropatico"
    }

    return f'''
    <html>
        <head><title>Risultato</title></head>
        <body>
            <h2>Risultato del questionario</h2>
            <p>Tipo di occhio secco più probabile: <strong>{tipo_full[tipo]}</strong></p>
            <p><a href="/questionario">Compila di nuovo</a></p>
        </body>
    </html>
    '''
