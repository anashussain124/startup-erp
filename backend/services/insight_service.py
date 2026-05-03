"""
Insight Service — Manages creation and retrieval of proactive insights.
"""
from sqlalchemy.orm import Session
from models.insight import Insight

def create_insight(db: Session, company_id: str, source: str, title: str, content: str, action: str = None, is_alert: bool = False):
    """Save a new insight to the database."""
    insight = Insight(
        company_id=company_id,
        source_type=source,
        title=title,
        content=content,
        action_item=action,
        is_alert=is_alert
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight

def get_latest_insights(db: Session, company_id: str, limit: int = 5):
    """Fetch the most recent insights for a company."""
    return db.query(Insight).filter(
        Insight.company_id == company_id
    ).order_by(Insight.created_at.desc()).limit(limit).all()
