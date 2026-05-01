"""
CRM Service — business logic for Customer, Lead, Sale.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.crm import Customer, Lead, Sale
from schemas.crm import (
    CustomerCreate, CustomerUpdate,
    LeadCreate, LeadUpdate,
    SaleCreate, SaleUpdate,
)


# ═══════════════════════════════════════════════════════════════════════════
# Customer CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_customer(db: Session, data: CustomerCreate) -> Customer:
    # Duplicate check
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise ValueError(f"Customer email '{data.email}' already exists")
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customers(db: Session, skip: int = 0, limit: int = 100, segment: str | None = None):
    q = db.query(Customer)
    if segment:
        q = q.filter(Customer.segment == segment)
    return q.offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def update_customer(db: Session, customer_id: int, data: CustomerUpdate) -> Customer | None:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer_id: int) -> bool:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return False
    db.delete(customer)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Lead CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_lead(db: Session, data: LeadCreate) -> Lead:
    lead = Lead(**data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_leads(db: Session, skip: int = 0, limit: int = 100, status: str | None = None):
    q = db.query(Lead)
    if status:
        q = q.filter(Lead.status == status)
    return q.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def get_lead(db: Session, lead_id: int) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead(db: Session, lead_id: int, data: LeadUpdate) -> Lead | None:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Sale CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_sale(db: Session, data: SaleCreate) -> Sale:
    sale = Sale(**data.model_dump())
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def get_sales(db: Session, skip: int = 0, limit: int = 100, customer_id: int | None = None):
    q = db.query(Sale)
    if customer_id:
        q = q.filter(Sale.customer_id == customer_id)
    return q.order_by(Sale.date.desc()).offset(skip).limit(limit).all()


def get_sale(db: Session, sale_id: int) -> Sale | None:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def update_sale(db: Session, sale_id: int, data: SaleUpdate) -> Sale | None:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sale, key, value)
    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale_id: int) -> bool:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        return False
    db.delete(sale)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Aggregation helpers
# ═══════════════════════════════════════════════════════════════════════════
def lead_pipeline(db: Session):
    """Return counts by lead status."""
    rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    return {status: count for status, count in rows}


def total_sales(db: Session, year: int | None = None) -> float:
    q = db.query(func.coalesce(func.sum(Sale.amount), 0))
    if year:
        q = q.filter(func.extract("year", Sale.date) == year)
    return float(q.scalar())
