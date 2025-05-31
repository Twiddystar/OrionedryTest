from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from datetime import datetime

app = FastAPI(title="Dry Eye Questionnaire API", version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class QuestionnaireAnswer(BaseModel):
    question_id: int
    value: str  # Can be "0"-"4" for scale questions or "si"/"no" for yes/no questions

class QuestionnaireSubmission(BaseModel):
    answers: Dict[str, str]
    timestamp: Optional[datetime] = None

class QuestionnaireResult(BaseModel):
    type: str
    description: str
    recommendations: List[str]
    scores: Dict[str, int]

# Classification algorithm
def classify_dry_eye(answers: Dict[str, str]) -> QuestionnaireResult:
    """
    Classifica il tipo di occhio secco basato sulle risposte del questionario
    
    Logica di classificazione:
    - Evaporativo: punteggi alti alle domande 2, 3, 5, 7, 14, 19
    - Deficit acquoso: domande 1, 6, 15, 16, 11, 18
    - Neuropatico: risposta positiva alla 20 con sintomi elevati
    - Misto: se entrambe le categorie precedenti hanno punteggi elevati
    """
    
    evaporative_questions = [2, 3, 5, 7, 14, 19]
    aqueous_deficit_questions = [1, 6, 15, 16, 11, 18]
    neuropathic_indicator = answers.get('20') == 'si'
    
    evaporative_score = 0
    aqueous_score = 0
    total_symptoms = 0

    # Calcola punteggio evaporativo
    for q in evaporative_questions:
        answer = answers.get(str(q), '0')
        if q <= 7:
            # Domande scala 0-4
            evaporative_score += int(answer)
        else:
            # Domande sì/no (sì = 2 punti, no = 0)
            evaporative_score += 2 if answer == 'si' else 0

    # Calcola punteggio deficit acquoso
    for q in aqueous_deficit_questions:
        answer = answers.get(str(q), '0')
        if q <= 7:
            # Domande scala 0-4
            aqueous_score += int(answer)
        else:
            # Domande sì/no (sì = 2 punti, no = 0)
            aqueous_score += 2 if answer == 'si' else 0

    # Calcola sintomi totali (domande 1-7)
    for i in range(1, 8):
        total_symptoms += int(answers.get(str(i), '0'))

    # Logica di classificazione
    if neuropathic_indicator and total_symptoms >= 15:
        return QuestionnaireResult(
            type="Occhio Secco Neuropatico",
            description="Il tuo profilo è compatibile con un occhio secco di tipo neuropatico. I sintomi sono intensi ma spesso l'esame oculistico può risultare normale o con pochi segni clinici visibili.",
            recommendations=[
                "Considera una valutazione neurologica specializzata",
                "Potrebbero essere utili terapie specifiche per il dolore neuropatico",
                "Mantieni un diario dei sintomi per identificare i trigger"
            ],
            scores={
                "evaporativeScore": evaporative_score,
                "aqueousScore": aqueous_score,
                "totalSymptoms": total_symptoms
            }
        )
    elif evaporative_score >= 12 and aqueous_score >= 10:
        return QuestionnaireResult(
            type="Occhio Secco Misto",
            description="Il tuo profilo presenta caratteristiche sia dell'occhio secco evaporativo che del deficit acquoso. Questa forma combinata richiede un approccio terapeutico multiplo.",
            recommendations=[
                "Combina impacchi caldi e lacrime artificiali",
                "Valuta igiene palpebrale quotidiana",
                "Potrebbero essere necessari diversi tipi di lacrime artificiali"
            ],
            scores={
                "evaporativeScore": evaporative_score,
                "aqueousScore": aqueous_score,
                "totalSymptoms": total_symptoms
            }
        )
    elif evaporative_score > aqueous_score and evaporative_score >= 8:
        return QuestionnaireResult(
            type="Occhio Secco Evaporativo",
            description="Il tuo profilo è compatibile con un occhio secco di tipo evaporativo, spesso legato alla disfunzione delle ghiandole di Meibomio che producono la componente oleosa delle lacrime.",
            recommendations=[
                "Impacchi caldi sulle palpebre 2 volte al giorno",
                "Massaggio delicato delle palpebre",
                "Igiene palpebrale con prodotti specifici",
                "Riduci l'uso prolungato di schermi digitali"
            ],
            scores={
                "evaporativeScore": evaporative_score,
                "aqueousScore": aqueous_score,
                "totalSymptoms": total_symptoms
            }
        )
    elif aqueous_score >= 8:
        return QuestionnaireResult(
            type="Occhio Secco da Deficit Acquoso",
            description="Il tuo profile è compatibile con un occhio secco da deficit acquoso, caratterizzato da una ridotta produzione della componente acquosa delle lacrime.",
            recommendations=[
                "Lacrime artificiali frequenti (senza conservanti se usate spesso)",
                "Considera lacrime più viscose per la notte",
                "Evita ambienti secchi o ventosi",
                "Valuta possibili farmaci che potrebbero influire sulla produzione lacrimale"
            ],
            scores={
                "evaporativeScore": evaporative_score,
                "aqueousScore": aqueous_score,
                "totalSymptoms": total_symptoms
            }
        )
    else:
        return QuestionnaireResult(
            type="Occhio Secco Lieve",
            description="I tuoi sintomi suggeriscono una forma lieve di occhio secco. Potrebbero essere sufficienti misure preventive e trattamenti semplici.",
            recommendations=[
                "Lacrime artificiali al bisogno",
                "Pause frequenti durante l'uso di schermi",
                "Mantieni una buona idratazione",
                "Controlla l'umidità degli ambienti dove passi più tempo"
            ],
            scores={
                "evaporativeScore": evaporative_score,
                "aqueousScore": aqueous_score,
                "totalSymptoms": total_symptoms
            }
        )

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Endpoint per verificare lo stato dell'API"""
    return {"status": "healthy", "message": "Dry Eye Questionnaire API is running"}

@app.post("/api/questionnaire/submit", response_model=QuestionnaireResult)
async def submit_questionnaire(submission: QuestionnaireSubmission):
    """
    Elabora le risposte del questionario e restituisce la classificazione
    """
    try:
        # Valida che ci siano abbastanza risposte
        if len(submission.answers) < 20:
            raise HTTPException(
                status_code=400, 
                detail="Questionario incompleto. Sono richieste risposte a tutte le 20 domande."
            )
        
        # Classifica il tipo di occhio secco
        result = classify_dry_eye(submission.answers)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Errore nei dati forniti: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno del server: {str(e)}")

@app.get("/api/questionnaire/questions")
async def get_questions():
    """
    Restituisce la struttura delle domande del questionario
    """
    return {
        "sections": [
            {
                "id": 1,
                "title": "Sintomi Principali",
                "description": "Valuta quanto spesso hai questi sintomi (da 0 = mai a 4 = sempre)",
                "questions": [
                    {"id": 1, "text": "I tuoi occhi ti sembrano secchi o irritati?", "type": "scale"},
                    {"id": 2, "text": "Senti bruciore o pizzicore agli occhi?", "type": "scale"},
                    {"id": 3, "text": "Hai sensazione di sabbia o corpo estraneo?", "type": "scale"},
                    {"id": 4, "text": "Avverti fastidio alla luce (fotofobia)?", "type": "scale"},
                    {"id": 5, "text": "La tua vista diventa offuscata nel corso della giornata?", "type": "scale"},
                    {"id": 6, "text": "I tuoi occhi lacrimano spontaneamente?", "type": "scale"},
                    {"id": 7, "text": "I sintomi peggiorano alla sera o dopo uso del computer?", "type": "scale"}
                ]
            },
            {
                "id": 2,
                "title": "Fattori Predisponenti",
                "description": "Rispondi Sì o No alle seguenti domande",
                "questions": [
                    {"id": 8, "text": "Usi frequentemente schermi (PC, tablet, smartphone)?", "type": "yesno"},
                    {"id": 9, "text": "Indossi lenti a contatto?", "type": "yesno"},
                    {"id": 10, "text": "Hai mai fatto un intervento agli occhi?", "type": "yesno"},
                    {"id": 11, "text": "Hai una malattia autoimmune diagnosticata (es. Sjögren, lupus)?", "type": "yesno"},
                    {"id": 12, "text": "Assumi farmaci per la pressione, depressione o antistaminici?", "type": "yesno"}
                ]
            },
            {
                "id": 3,
                "title": "Risposte ai Trattamenti",
                "description": "Indica se hai notato miglioramenti con questi trattamenti",
                "questions": [
                    {"id": 13, "text": "Noti miglioramento con lacrime artificiali?", "type": "yesno"},
                    {"id": 14, "text": "Noti miglioramento dopo impacchi caldi?", "type": "yesno"},
                    {"id": 15, "text": "I sintomi compaiono soprattutto al risveglio?", "type": "yesno"},
                    {"id": 16, "text": "Hai provato lacrime più viscose o gel, con miglioramento?", "type": "yesno"}
                ]
            },
            {
                "id": 4,
                "title": "Diagnostica Riferita",
                "description": "Indica se conosci questi aspetti della tua condizione",
                "questions": [
                    {"id": 17, "text": "Ti hanno mai detto che hai un film lacrimale instabile?", "type": "yesno"},
                    {"id": 18, "text": "Ti hanno mai fatto il test di Schirmer (carta sotto la palpebra)?", "type": "yesno"},
                    {"id": 19, "text": "Sai se le tue ghiandole di Meibomio funzionano bene (MGD)?", "type": "yesno"},
                    {"id": 20, "text": "I tuoi sintomi sono molto forti anche se all'esame l'occhio è 'normale'?", "type": "yesno"}
                ]
            }
        ]
    }

@app.get("/api/questionnaire/info")
async def get_questionnaire_info():
    """
    Restituisce informazioni generali sul questionario
    """
    return {
        "title": "Questionario per la Classificazione dell'Occhio Secco",
        "description": "Questo questionario ti aiuterà a identificare il tipo di occhio secco che potresti avere.",
        "total_questions": 20,
        "sections": 4,
        "estimated_time": "5-10 minuti",
        "disclaimer": "Questo risultato non sostituisce una valutazione medica. Porta con te questo risultato alla visita oculistica."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)