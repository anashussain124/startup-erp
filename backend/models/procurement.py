"""
Procurement models — Vendor, PurchaseOrder, InventoryItem.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    rating = Column(Float, default=3.0)  # 1.0 - 5.0
    is_active = Column(Integer, default=1)
    company_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    inventory_items = relationship("InventoryItem", back_populates="vendor")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_number = Column(String(30), unique=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    items_description = Column(Text, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending | approved | shipped | delivered | cancelled
    order_date = Column(Date, nullable=False)
    expected_delivery = Column(Date, nullable=True)
    company_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="purchase_orders")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    unit_price = Column(Float, nullable=False)
    reorder_level = Column(Integer, default=10)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    category = Column(String(50), nullable=True)
    company_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Vendor", back_populates="inventory_items")
