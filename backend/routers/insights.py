"""
Insights Router — Fetch proactive business intelligence.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.dependencies import get_current_user
from services.insight_service import get_latest_insights

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/latest")
def list_latest_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch the latest proactive insights for the dashboard."""
    return get_latest_insights(db, current_user.company_id)
