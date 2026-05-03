"""
Insight model — stores proactive AI-generated suggestions and analytics.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)
    source_type = Column(String(20), nullable=False) # doc | query | general
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    action_item = Column(String(255), nullable=True) # "Reduce marketing", "Check payroll"
    is_alert = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
