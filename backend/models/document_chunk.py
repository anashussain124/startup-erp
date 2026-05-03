"""
DocumentChunk model — stores text segments for better AI context management.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("company_documents.id"), nullable=False)
    company_id = Column(String(50), nullable=False, index=True)
    text_content = Column(Text, nullable=False)
