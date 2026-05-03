"""
Company model — handles billing, plans, and usage limits.
"""
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.sql import func
from database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String(50), primary_key=True, index=True) # slug or unique ID
    name = Column(String(100), nullable=False)
    plan = Column(String(20), default="free") # free | pro
    ai_queries_today = Column(Integer, default=0)
    last_query_date = Column(Date, server_default=func.current_date())
