"""
CompanyDocument model — stores metadata and extracted text for AI context.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class CompanyDocument(Base):
    __tablename__ = "company_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf | docx | csv
    storage_path = Column(String(512), nullable=False)  # Path in Supabase Storage
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True) # Auto-generated summary
    uploaded_by = Column(Integer, nullable=False)  # User ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
