"""
Billing Router — Fetch usage stats and plan info.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.company import Company
from models.document import CompanyDocument
from auth.dependencies import get_current_user
from services.billing_service import get_or_create_company

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/stats")
def get_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return usage statistics for the current company."""
    company = get_or_create_company(db, current_user.company_id)
    doc_count = db.query(CompanyDocument).filter(CompanyDocument.company_id == current_user.company_id).count()
    
    return {
        "plan": company.plan,
        "docs_used": doc_count,
        "docs_limit": 5 if company.plan == "free" else 999,
        "ai_queries_today": company.ai_queries_today,
        "ai_limit": 10 if company.plan == "free" else 999
    }
