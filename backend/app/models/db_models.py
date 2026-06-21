# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_path = Column(String)
    doc_type = Column(String, default="Unknown") # "HR Policy", "Vendor Contract", "Security SOP"
    upload_date = Column(DateTime, default=datetime.utcnow)
    page_count = Column(Integer, default=0)
    status = Column(String, default="processing") # "processing", "indexed", "failed"

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    risks = relationship("RiskMatch", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    page_number = Column(Integer)
    content = Column(String)
    vector_index = Column(Integer, index=True)

    document = relationship("Document", back_populates="chunks")

class RiskMatch(Base):
    __tablename__ = "risk_matches"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    clause_text = Column(String)
    rule_id = Column(String)
    category = Column(String) # "Liability", "Term", "Compliance"
    severity = Column(String) # "High", "Medium", "Low"
    source = Column(String) # "Rule", "ML"
    confidence = Column(Float) # probability score
    page_number = Column(Integer)

    document = relationship("Document", back_populates="risks")
