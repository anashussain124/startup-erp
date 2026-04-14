"""
CRM models — Customer, Lead, Sale.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    segment = Column(String(30), nullable=True)  # enterprise | smb | startup | individual
    lifetime_value = Column(Float, default=0.0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    leads = relationship("Lead", back_populates="customer", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    contact_name = Column(String(100), nullable=False)
    contact_email = Column(String(100), nullable=True)
    source = Column(String(50), nullable=True)  # website | referral | social | ads | cold_call
    status = Column(String(20), nullable=False, default="new")  # new | contacted | qualified | proposal | converted | lost
    estimated_value = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="leads")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    product_description = Column(String(200), nullable=True)
    payment_status = Column(String(20), default="pending")  # pending | paid | overdue
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="sales")
