"""
CRM schemas — Customer, Lead, Sale.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ── Customer ─────────────────────────────────────────────────────────────────
class CustomerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    phone: Optional[str] = None
    company: Optional[str] = None
    segment: Optional[str] = Field(default=None, pattern="^(enterprise|smb|startup|individual)$")
    lifetime_value: float = Field(default=0.0, ge=0)


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    segment: Optional[str] = Field(default=None, pattern="^(enterprise|smb|startup|individual)$")
    lifetime_value: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[int] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    segment: Optional[str] = None
    lifetime_value: float
    is_active: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Lead ─────────────────────────────────────────────────────────────────────
class LeadCreate(BaseModel):
    customer_id: Optional[int] = None
    contact_name: str = Field(..., max_length=100)
    contact_email: Optional[str] = None
    source: Optional[str] = None
    status: str = Field(default="new", pattern="^(new|contacted|qualified|proposal|converted|lost)$")
    estimated_value: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    customer_id: Optional[int] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(new|contacted|qualified|proposal|converted|lost)$")
    estimated_value: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None


class LeadOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    contact_name: str
    contact_email: Optional[str] = None
    source: Optional[str] = None
    status: str
    estimated_value: float
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Sale ─────────────────────────────────────────────────────────────────────
class SaleCreate(BaseModel):
    customer_id: int
    amount: float = Field(..., gt=0)
    date: date
    product_description: Optional[str] = None
    payment_status: str = Field(default="pending", pattern="^(pending|paid|overdue)$")


class SaleUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    date: Optional[date] = None
    product_description: Optional[str] = None
    payment_status: Optional[str] = Field(default=None, pattern="^(pending|paid|overdue)$")


class SaleOut(BaseModel):
    id: int
    customer_id: int
    amount: float
    date: date
    product_description: Optional[str] = None
    payment_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
