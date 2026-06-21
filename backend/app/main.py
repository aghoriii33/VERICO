# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine, Base
from app.api import documents, qa
from app.services.embedder import Embedder
from app.services.qa_engine import QAEngine
from app.services.risk_classifier import RiskClassifier

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VERICO — Smart Document Intelligence & Compliance QA API",
    description="Compliance assistant for multi-document extractive Q&A and risk detection.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents.router)
app.include_router(qa.router)

@app.on_event("startup")
def startup_event():
    print("Initializing VERICO Backend Services...")
    # Pre-load ML models and rules so they are warm for the first request
    try:
        RiskClassifier.load_rules()
        RiskClassifier.load_ml_model()
        Embedder.get_instance()
        QAEngine.get_pipeline()
        print("All models and rules pre-loaded successfully.")
    except Exception as e:
        print(f"Warning: Failed to pre-load some models: {e}")

@app.get("/")
def read_root():
    return {
        "app": "VERICO Compliance API",
        "status": "online",
        "version": "1.0.0"
    }
