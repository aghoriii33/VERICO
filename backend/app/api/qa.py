from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.models.db_models import Document, DocumentChunk
from app.services.vector_store import VectorStore
from app.services.qa_engine import QAEngine
from app.config import TOP_K_CHUNKS

router = APIRouter(prefix="/api/qa", tags=["qa"])

class QueryRequest(BaseModel):
    question: str
    document_ids: Optional[List[int]] = None

class AlternativeAnswer(BaseModel):
    answer: str
    score: float
    document_name: Optional[str] = None
    page_number: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    score: float
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    context: Optional[str] = None
    start: int
    end: int
    alternatives: List[AlternativeAnswer] = []

@router.post("/query", response_model=QueryResponse)
def query_compliance_documents(req: QueryRequest, db: Session = Depends(get_db)):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Search the FAISS index for relevant chunks
    # Retrieve more chunks initially (e.g. 50) if document filter is present, to ensure matches
    search_k = 50 if req.document_ids else 15
    search_results = VectorStore.search(req.question, k=search_k)
    
    if not search_results:
        return QueryResponse(
            answer="No documents have been indexed yet. Please upload files first.",
            score=0.0,
            start=0,
            end=0
        )

    # 2. Map FAISS indices to database chunks
    vector_indices = [idx for idx, score in search_results]
    score_map = {idx: score for idx, score in search_results}

    chunks_query = db.query(DocumentChunk).filter(DocumentChunk.vector_index.in_(vector_indices))
    
    # Apply document ID filter if specified
    if req.document_ids:
        chunks_query = chunks_query.filter(DocumentChunk.document_id.in_(req.document_ids))
        
    db_chunks = chunks_query.all()
    
    if not db_chunks:
        return QueryResponse(
            answer="No relevant passages found in the selected documents.",
            score=0.0,
            start=0,
            end=0
        )

    # 3. Sort retrieved chunks by their original similarity score
    chunk_scores = []
    for chunk in db_chunks:
        score = score_map.get(int(chunk.vector_index), 0.0)
        chunk_scores.append((chunk, score))
    
    chunk_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Select top k chunks
    top_chunks = chunk_scores[:TOP_K_CHUNKS]
    
    # 4. Prepare passages for the QA Engine
    passages = []
    for chunk, score in top_chunks:
        doc = db.query(Document).filter(Document.id == chunk.document_id).first()
        passages.append({
            "content": chunk.content,
            "document_name": doc.filename if doc else "Unknown",
            "page_number": chunk.page_number
        })

    # 5. Extract answers from passages using the QA model
    best_answer = QAEngine.answer_question(req.question, passages)
    
    # Re-map alternatives to Pydantic model format
    alternatives = []
    for alt in best_answer.get("alternatives", []):
        alternatives.append(AlternativeAnswer(
            answer=alt["answer"],
            score=alt["score"],
            document_name=alt["document_name"],
            page_number=alt["page_number"]
        ))

    return QueryResponse(
        answer=best_answer["answer"],
        score=best_answer["score"],
        document_name=best_answer["document_name"],
        page_number=best_answer["page_number"],
        context=best_answer["context"],
        start=best_answer["start"],
        end=best_answer["end"],
        alternatives=alternatives
    )
