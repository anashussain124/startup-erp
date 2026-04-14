"""
Procurement schemas — Vendor, PurchaseOrder, InventoryItem.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ── Vendor ───────────────────────────────────────────────────────────────────
class VendorCreate(BaseModel):
    name: str = Field(..., max_length=100)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: float = Field(default=3.0, ge=1.0, le=5.0)


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    is_active: Optional[int] = None


class VendorOut(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: float
    is_active: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── PurchaseOrder ────────────────────────────────────────────────────────────
class PurchaseOrderCreate(BaseModel):
    po_number: str = Field(..., max_length=30)
    vendor_id: int
    items_description: str
    total_amount: float = Field(..., gt=0)
    status: str = Field(default="pending", pattern="^(pending|approved|shipped|delivered|cancelled)$")
    order_date: date
    expected_delivery: Optional[date] = None


class PurchaseOrderUpdate(BaseModel):
    items_description: Optional[str] = None
    total_amount: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = Field(default=None, pattern="^(pending|approved|shipped|delivered|cancelled)$")
    expected_delivery: Optional[date] = None


class PurchaseOrderOut(BaseModel):
    id: int
    po_number: str
    vendor_id: int
    items_description: str
    total_amount: float
    status: str
    order_date: date
    expected_delivery: Optional[date] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── InventoryItem ────────────────────────────────────────────────────────────
class InventoryItemCreate(BaseModel):
    name: str = Field(..., max_length=100)
    sku: str = Field(..., max_length=50)
    quantity: int = Field(default=0, ge=0)
    unit_price: float = Field(..., gt=0)
    reorder_level: int = Field(default=10, ge=0)
    vendor_id: Optional[int] = None
    category: Optional[str] = None


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    unit_price: Optional[float] = Field(default=None, gt=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    vendor_id: Optional[int] = None
    category: Optional[str] = None


class InventoryItemOut(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int
    unit_price: float
    reorder_level: int
    vendor_id: Optional[int] = None
    category: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
