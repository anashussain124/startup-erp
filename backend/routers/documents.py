from auth.dependencies import get_current_user, require_role
from services.supabase_service import upload_to_supabase
from services.extraction_service import extract_text
from services.billing_service import check_billing_limits
from services.ai_service import chunk_text, generate_summary, generate_document_insights
from services.insight_service import create_insight
from models.document_chunk import DocumentChunk
import uuid

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    """Upload a document, chunk it, summarize it, and generate proactive insights."""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")

    # 1. Billing Check
    check_billing_limits(db, current_user.company_id, "upload")

    content = await file.read()
    
    # 2. Extract text
    text = extract_text(content, file.filename)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    # 3. Auto-Insight (Summary & Key Points)
    summary = generate_summary(text)
    extra_insights = generate_document_insights(text)

    # 4. Save Proactive Insights to DB
    create_insight(
        db, 
        current_user.company_id, 
        "doc", 
        f"Insights: {file.filename}", 
        ", ".join(extra_insights.get("insights", [])),
        action="Review document highlights in Knowledge Base."
    )

    # 5. Upload to Supabase Storage
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    storage_path = f"{current_user.company_id}/{unique_filename}"
    
    upload_res = upload_to_supabase("company-docs", storage_path, content)
    if not upload_res:
        raise HTTPException(status_code=500, detail="Failed to upload to storage")

    # 6. Save to DB
    doc = CompanyDocument(
        company_id=current_user.company_id,
        filename=file.filename,
        file_type=file.filename.split(".")[-1].lower(),
        storage_path=storage_path,
        extracted_text=text,
        summary=summary,
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 7. Store Chunks
    chunks = chunk_text(text)
    for c_text in chunks:
        chunk = DocumentChunk(
            document_id=doc.id,
            company_id=current_user.company_id,
            text_content=c_text
        )
        db.add(chunk)
    db.commit()

    return {"message": "File processed with proactive insights", "id": doc.id, "summary": summary}

@router.get("/list")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents for the user's company."""
    docs = db.query(CompanyDocument).filter(
        CompanyDocument.company_id == current_user.company_id
    ).all()
    return docs
