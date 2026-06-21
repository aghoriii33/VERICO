# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import shutil
import os
from datetime import datetime

from app.database import get_db
from app.models.db_models import Document, DocumentChunk, RiskMatch
from app.config import DOCUMENTS_DIR
from app.services.parser import PDFParser
from app.services.chunker import Chunker
from app.services.vector_store import VectorStore
from app.services.risk_classifier import RiskClassifier

router = APIRouter(prefix="/api/documents", tags=["documents"])

def sync_vector_store(db: Session):
    """
    Rebuilds the FAISS vector index from all active document chunks in the database
    and updates their vector_index alignment values.
    """
    db_chunks = db.query(DocumentChunk).order_by(DocumentChunk.id).all()
    chunks_list = [{"id": c.id, "content": c.content} for c in db_chunks]
    
    # Rebuild FAISS index
    VectorStore.rebuild_index(chunks_list)
    
    # Update SQLite records with the aligned index
    for idx, chunk in enumerate(db_chunks):
        chunk.vector_index = idx
    db.commit()

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    uploaded_results = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            uploaded_results.append({"filename": file.filename, "status": "failed", "error": "Only PDF files are supported."})
            continue
            
        file_path = os.path.join(DOCUMENTS_DIR, file.filename)
        
        # Save file to disk
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        except Exception as e:
            uploaded_results.append({"filename": file.filename, "status": "failed", "error": f"Failed to save file: {str(e)}"})
            continue
            
        # Parse PDF
        try:
            pages = PDFParser.extract_text_by_page(file_path)
            if not pages:
                uploaded_results.append({"filename": file.filename, "status": "failed", "error": "No readable text found in PDF."})
                os.remove(file_path)
                continue
                
            full_text = " ".join(p[1] for p in pages)
            doc_type = PDFParser.detect_document_type(file.filename, full_text)
            
            # Check if document already exists
            existing_doc = db.query(Document).filter(Document.filename == file.filename).first()
            if existing_doc:
                # Delete existing doc first to update
                db.delete(existing_doc)
                db.commit()
                
            # Create Document metadata
            db_doc = Document(
                filename=file.filename,
                file_path=file_path,
                doc_type=doc_type,
                page_count=len(pages),
                status="processing"
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)
            
            # Chunk document
            pages_list = [{"page_number": p[0], "text": p[1]} for p in pages]
            chunks = Chunker.chunk_document(pages_list)
            
            # Save chunks to DB
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
            
            # Scan for risks
            detected_risks = []
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
                    detected_risks.append(r)
            db.commit()
            
            # Update doc status
            db_doc.status = "indexed"
            db.commit()
            
            uploaded_results.append({
                "id": db_doc.id,
                "filename": db_doc.filename,
                "status": "success",
                "doc_type": db_doc.doc_type,
                "page_count": db_doc.page_count,
                "risks_found": len(detected_risks)
            })
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            uploaded_results.append({"filename": file.filename, "status": "failed", "error": f"Internal process error: {str(e)}"})
            db.rollback()
            continue
            
    # Sync FAISS vector store with all chunks
    try:
        sync_vector_store(db)
    except Exception as e:
        print(f"Error building vector store: {e}")
        
    return uploaded_results

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    results = []
    
    for doc in docs:
        # Aggregate risks counts
        risks = db.query(RiskMatch).filter(RiskMatch.document_id == doc.id).all()
        risk_counts = {"High": 0, "Medium": 0, "Low": 0}
        for r in risks:
            sev = str(r.severity)
            risk_counts[sev] = risk_counts.get(sev, 0) + 1
            
        results.append({
            "id": doc.id,
            "filename": doc.filename,
            "file_path": doc.file_path,
            "doc_type": doc.doc_type,
            "upload_date": doc.upload_date.isoformat(),
            "page_count": doc.page_count,
            "status": doc.status,
            "risks_summary": risk_counts,
            "total_risks": len(risks)
        })
    return results

@router.get("/risks")
def list_all_risks(db: Session = Depends(get_db)):
    """
    Lists all detected risks across all documents for the Analytics panel.
    """
    risks = db.query(RiskMatch).all()
    results = []
    for r in risks:
        doc = db.query(Document).filter(Document.id == r.document_id).first()
        results.append({
            "id": r.id,
            "document_id": r.document_id,
            "document_name": doc.filename if doc else "Deleted Document",
            "document_type": doc.doc_type if doc else "Unknown",
            "clause_text": r.clause_text,
            "rule_id": r.rule_id,
            "category": r.category,
            "severity": r.severity,
            "source": r.source,
            "confidence": r.confidence,
            "page_number": r.page_number
        })
    return results

@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    risks = db.query(RiskMatch).filter(RiskMatch.document_id == doc_id).all()
    risk_list = [{
        "id": r.id,
        "clause_text": r.clause_text,
        "rule_id": r.rule_id,
        "category": r.category,
        "severity": r.severity,
        "source": r.source,
        "confidence": r.confidence,
        "page_number": r.page_number
    } for r in risks]
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "upload_date": doc.upload_date.isoformat(),
        "page_count": doc.page_count,
        "status": doc.status,
        "risks": risk_list
    }

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
        
    # Delete PDF file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Error removing document file: {e}")
            
    db.delete(doc)
    db.commit()
    
    # Sync FAISS vector store (rebuild without the deleted chunks)
    sync_vector_store(db)
    
    return {"status": "success", "message": f"Document {doc_id} deleted successfully."}

@router.post("/rebuild-index")
def rebuild_vector_index(db: Session = Depends(get_db)):
    try:
        sync_vector_store(db)
        return {"status": "success", "message": "FAISS vector store index rebuilt successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")
