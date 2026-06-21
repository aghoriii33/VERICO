import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
MODELS_DIR = BASE_DIR / "app" / "models"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR}/compliance_qa.db"

# Vector Store and Model Config
FAISS_INDEX_PATH = str(DATA_DIR / "faiss_index")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
QA_MODEL_NAME = "deepset/tinyroberta-squad2"

# Risk Detection Config
RISK_RULES_PATH = str(DATA_DIR / "risk_rules.yaml")
RISK_CLASSIFIER_PATH = str(MODELS_DIR / "risk_classifier.pkl")

# RAG configuration
TOP_K_CHUNKS = 3
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
