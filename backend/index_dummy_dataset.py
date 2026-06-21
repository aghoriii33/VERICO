import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from app.database import Base, engine, SessionLocal
from app.models.db_models import Document, DocumentChunk, RiskMatch
from app.config import DOCUMENTS_DIR
from app.services.parser import PDFParser
from app.services.chunker import Chunker
from app.services.vector_store import VectorStore
from app.services.risk_classifier import RiskClassifier

def index_all_documents():
    print("====================================================")
    print("Indexing Dummy Dataset into VERICO Database...")
    print("====================================================")

    # Initialize Database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Get all PDF files in the documents directory
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("Error: No PDF files found to index. Run generate_dummy_dataset.py first.")
        db.close()
        return False

    print(f"Found {len(pdf_files)} PDF files to index.")

    for pdf_path in pdf_files:
        filename = pdf_path.name
        print(f"\nProcessing {filename}...")

        # Check if already exists, skip or recreate
        existing_doc = db.query(Document).filter(Document.filename == filename).first()
        if existing_doc:
            print(f"  {filename} already indexed in DB. Re-indexing...")
            db.delete(existing_doc)
            db.commit()

        try:
            # 1. Parse text from PDF
            pages = PDFParser.extract_text_by_page(str(pdf_path))
            if not pages:
                print(f"  Warning: No readable text in {filename}. Skipping.")
                continue

            full_text = " ".join(p[1] for p in pages)
            doc_type = PDFParser.detect_document_type(filename, full_text)

            # 2. Save Document metadata
            db_doc = Document(
                filename=filename,
                file_path=str(pdf_path),
                doc_type=doc_type,
                page_count=len(pages),
                status="processing"
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            # 3. Chunk the text
            pages_list = [{"page_number": p[0], "text": p[1]} for p in pages]
            chunks = Chunker.chunk_document(pages_list)

            # 4. Save Chunks
            db_chunks = []
            for chunk in chunks:
                db_chunk = DocumentChunk(
                    document_id=db_doc.id,
                    page_number=chunk["page_number"],
                    content=chunk["content"]
                )
                db.add(db_chunk)
                db_chunks.append(db_chunk)
            db.commit()

            # 5. Scan for Risks (Rule + ML)
            detected_risks = 0
            for chunk in db_chunks:
                risks = RiskClassifier.scan_chunk(chunk.content, chunk.page_number)
                for r in risks:
                    risk_match = RiskMatch(
                        document_id=db_doc.id,
                        clause_text=r["clause_text"],
                        rule_id=r["rule_id"],
                        category=r["category"],
                        severity=r["severity"],
                        source=r["source"],
                        confidence=r["confidence"],
                        page_number=r["page_number"]
                    )
                    db.add(risk_match)
                    detected_risks += 1
            db.commit()

            # 6. Update Status
            db_doc.status = "indexed"
            db.commit()
            print(f"  Successfully indexed. Chunks: {len(db_chunks)}, Risks found: {detected_risks}")

        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            db.rollback()
            continue

    # 7. Rebuild FAISS index
    print("\nRebuilding FAISS index from scratch...")
    try:
        db_chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).all()
        chunks_list = [{"id": c.id, "content": c.content} for c in db_chunks]
        
        VectorStore.rebuild_index(chunks_list)
        
        # Align index
        for idx, chunk in enumerate(db_chunks):
            chunk.vector_index = idx
        db.commit()
        print("FAISS index successfully built and aligned.")
    except Exception as e:
        print(f"Error building FAISS index: {e}")

    db.close()
    print("\n====================================================")
    print("Indexing Complete!")
    print("====================================================")
    return True

if __name__ == "__main__":
    index_all_documents()
