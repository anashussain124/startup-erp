"""
Extraction Service — Extracts text from various file formats.
"""
import io
import PyPDF2
from docx import Document

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX bytes."""
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"DOCX Extraction Error: {e}")
        return ""

def extract_text(file_content: bytes, filename: str) -> str:
    """General text extraction based on file extension."""
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_content)
    elif ext == "docx":
        return extract_text_from_docx(file_content)
    elif ext in ["csv", "txt"]:
        return file_content.decode("utf-8", errors="ignore")
    return ""
