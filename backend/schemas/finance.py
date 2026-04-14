"""
Finance schemas — Expense, Revenue.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ── Expense ──────────────────────────────────────────────────────────────────
class ExpenseCreate(BaseModel):
    category: str = Field(..., max_length=50)
    amount: float = Field(..., gt=0)
    date: date
    description: Optional[str] = None
    approved_by: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    date: Optional[date] = None
    description: Optional[str] = None
    approved_by: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    category: str
    amount: float
    date: date
    description: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Revenue ──────────────────────────────────────────────────────────────────
class RevenueCreate(BaseModel):
    source: str = Field(..., max_length=100)
    amount: float = Field(..., gt=0)
    date: date
    description: Optional[str] = None


class RevenueUpdate(BaseModel):
    source: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    date: Optional[date] = None
    description: Optional[str] = None


class RevenueOut(BaseModel):
    id: int
    source: str
    amount: float
    date: date
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
