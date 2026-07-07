from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies import get_db
from app.routers import chants, paroisses, programmes

app = FastAPI(
    title="EMBERC API",
    description="API de la plateforme numérique de l'Église Mission Baptiste Évangélique Royaume du Christ",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API EMBERC", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT version()")).fetchone()
    return {"database": "connectée", "version": result[0]}


app.include_router(chants.router)
app.include_router(paroisses.router)
app.include_router(programmes.router)