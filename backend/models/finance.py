"""
Finance models — Expense, Revenue.
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # payroll | rent | marketing | utilities | supplies | other
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Revenue(Base):
    __tablename__ = "revenue"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)
    source = Column(String(100), nullable=False)  # product_sales | services | subscriptions | other
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
