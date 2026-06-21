# pyrefly: ignore [missing-import]
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent))

def run_integration_test():
    print("====================================================")
    print("Running VERICO Backend Services Integration Test...")
    print("====================================================")
    
    try:
        from app.database import engine, Base, SessionLocal
        from app.models.db_models import Document, DocumentChunk, RiskMatch
        from app.services.parser import PDFParser
        from app.services.chunker import Chunker
        from app.services.embedder import Embedder
        from app.services.vector_store import VectorStore
        from app.services.qa_engine import QAEngine
        from app.services.risk_classifier import RiskClassifier
        import numpy as np
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please ensure virtual environment packages are fully installed.")
        return False

    # 1. Initialize DB tables
    print("\n[Step 1] Initializing SQLite Database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("Database tables initialized successfully.")

    # 2. Check risk rules loading
    print("\n[Step 2] Testing Risk Classifier Rules Loading...")
    rules = RiskClassifier.load_rules()
    print(f"Loaded {len(rules)} compliance rules.")
    if len(rules) == 0:
        print("Error: Rules list is empty.")
        return False

    # 3. Test text chunking
    print("\n[Step 3] Testing Text Chunker...")
    sample_pages = [
        {"page_number": 1, "text": "This is paragraph one of the sample agreement. It contains standard licensing terms. " * 10},
        {"page_number": 2, "text": "This is page two. The vendor requires unlimited liability for all client operations. Tacit renewal applies, so the contract will renew automatically."}
    ]
    chunks = Chunker.chunk_document(sample_pages, chunk_size=20, chunk_overlap=5)
    print(f"Generated {len(chunks)} text chunks.")
    print(f"First chunk content: '{chunks[0]['content'][:60]}...'")

    # 4. Test Embedder (CPU)
    print("\n[Step 4] Testing Embedding Generator...")
    emb = Embedder.embed_query("unlimited liability")
    print(f"Embedding shape: {emb.shape}")
    if emb.shape[0] != 384:
        print("Error: Embedding dimension mismatch (expected 384).")
        return False

    # 5. Test Risk Scanning
    print("\n[Step 5] Testing Clause Risk Scanning...")
    clause1 = "The Vendor requires unlimited liability for damages."
    risks1 = RiskClassifier.scan_chunk(clause1, 2)
    print(f"Scanning text: '{clause1}'")
    print(f"Risks found: {risks1}")
    
    # 6. Test QA Engine
    print("\n[Step 6] Testing Extractive QA Engine...")
    sample_passages = [
        {
            "content": "Our social media policy requires employees to respect client confidentiality. Violations lead to termination.",
            "document_name": "HR_Policy_04.pdf",
            "page_number": 1
        },
        {
            "content": "The password complexity SOP requires all user accounts to use passwords of at least 12 characters with symbols.",
            "document_name": "Security_SOP_01.pdf",
            "page_number": 1
        }
    ]
    
    q1 = "What is the password length requirement?"
    print(f"Asking: '{q1}'")
    ans1 = QAEngine.answer_question(q1, sample_passages)
    print(f"Answer: '{ans1['answer']}' (Confidence: {ans1['score']:.4f})")
    print(f"Citation: {ans1['document_name']}, Page {ans1['page_number']}")
    
    print("\n====================================================")
    print("VERICO Backend Integration Test Completed Successfully!")
    print("====================================================")
    db.close()
    return True

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
