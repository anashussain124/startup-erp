"""
Billing Service — Enforces plan limits and tracks usage.
"""
from sqlalchemy.orm import Session
from models.company import Company
from models.document import CompanyDocument
from datetime import date
from fastapi import HTTPException

def get_or_create_company(db: Session, company_id: str):
    """Ensure company exists in our tracking table."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        company = Company(id=company_id, name=company_id)
        db.add(company)
        db.commit()
        db.refresh(company)
    return company

def check_billing_limits(db: Session, company_id: str, action: str):
    """
    Check if company has exceeded its plan limits.
    action: 'upload' | 'ai_query'
    """
    company = get_or_create_company(db, company_id)
    
    if company.plan == "free":
        if action == "upload":
            doc_count = db.query(CompanyDocument).filter(CompanyDocument.company_id == company_id).count()
            if doc_count >= 5:
                raise HTTPException(status_code=403, detail="Free plan limit reached (5 documents). Please upgrade to Pro.")
        
        elif action == "ai_query":
            # Reset counter if it's a new day
            if company.last_query_date != date.today():
                company.ai_queries_today = 0
                company.last_query_date = date.today()
                db.commit()
            
            if company.ai_queries_today >= 10:
                raise HTTPException(status_code=403, detail="Daily AI query limit reached (10 queries). Please upgrade to Pro.")

def increment_usage(db: Session, company_id: str, action: str):
    """Track usage after a successful action."""
    company = get_or_create_company(db, company_id)
    if action == "ai_query":
        company.ai_queries_today += 1
        db.commit()
