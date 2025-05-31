from fastapi import FastAPI
from backend.server import app as dry_eye_app

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Dry Eye Questionnaire API is live!"}

# Monta l'app principale
app.mount("/api", dry_eye_app)
