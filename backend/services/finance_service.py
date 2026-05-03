"""
Finance Service — business logic for Expense, Revenue.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.finance import Expense, Revenue
from schemas.finance import (
    ExpenseCreate, ExpenseUpdate,
    RevenueCreate, RevenueUpdate,
)
from datetime import date


# ═══════════════════════════════════════════════════════════════════════════
# Expense CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_expense(db: Session, data: ExpenseCreate, company_id: str) -> Expense:
    record = Expense(**data.model_dump(), company_id=company_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_expenses(db: Session, company_id: str, skip: int = 0, limit: int = 100, category: str | None = None):
    q = db.query(Expense).filter(Expense.company_id == company_id)
    if category:
        q = q.filter(Expense.category == category)
    return q.order_by(Expense.date.desc()).offset(skip).limit(limit).all()


def get_expense(db: Session, expense_id: int, company_id: str) -> Expense | None:
    return db.query(Expense).filter(Expense.id == expense_id, Expense.company_id == company_id).first()


def update_expense(db: Session, expense_id: int, data: ExpenseUpdate, company_id: str) -> Expense | None:
    record = db.query(Expense).filter(Expense.id == expense_id, Expense.company_id == company_id).first()
    if not record:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_expense(db: Session, expense_id: int, company_id: str) -> bool:
    record = db.query(Expense).filter(Expense.id == expense_id, Expense.company_id == company_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Revenue CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_revenue(db: Session, data: RevenueCreate, company_id: str) -> Revenue:
    record = Revenue(**data.model_dump(), company_id=company_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_revenues(db: Session, company_id: str, skip: int = 0, limit: int = 100, source: str | None = None):
    q = db.query(Revenue).filter(Revenue.company_id == company_id)
    if source:
        q = q.filter(Revenue.source == source)
    return q.order_by(Revenue.date.desc()).offset(skip).limit(limit).all()


def get_revenue(db: Session, revenue_id: int, company_id: str) -> Revenue | None:
    return db.query(Revenue).filter(Revenue.id == revenue_id, Revenue.company_id == company_id).first()


def update_revenue(db: Session, revenue_id: int, data: RevenueUpdate, company_id: str) -> Revenue | None:
    record = db.query(Revenue).filter(Revenue.id == revenue_id, Revenue.company_id == company_id).first()
    if not record:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_revenue(db: Session, revenue_id: int, company_id: str) -> bool:
    record = db.query(Revenue).filter(Revenue.id == revenue_id, Revenue.company_id == company_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Aggregation helpers (for dashboard)
# ═══════════════════════════════════════════════════════════════════════════
def total_expenses(db: Session, year: int | None = None, company_id: str = None) -> float:
    q = db.query(func.coalesce(func.sum(Expense.amount), 0))
    if company_id:
        q = q.filter(Expense.company_id == company_id)
    if year:
        q = q.filter(func.extract("year", Expense.date) == year)
    return float(q.scalar())


def total_revenue(db: Session, year: int | None = None, company_id: str = None) -> float:
    q = db.query(func.coalesce(func.sum(Revenue.amount), 0))
    if company_id:
        q = q.filter(Revenue.company_id == company_id)
    if year:
        q = q.filter(func.extract("year", Revenue.date) == year)
    return float(q.scalar())


def monthly_revenue(db: Session, year: int, company_id: str):
    """Return list of (month, total) tuples for the given year."""
    rows = (
        db.query(
            func.extract("month", Revenue.date).label("month"),
            func.sum(Revenue.amount).label("total"),
        )
        .filter(Revenue.company_id == company_id, func.extract("year", Revenue.date) == year)
        .group_by(func.extract("month", Revenue.date))
        .order_by(func.extract("month", Revenue.date))
        .all()
    )
    return [(int(r.month), float(r.total)) for r in rows]


def monthly_expenses(db: Session, year: int, company_id: str):
    """Return list of (month, total) tuples for the given year."""
    rows = (
        db.query(
            func.extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.company_id == company_id, func.extract("year", Expense.date) == year)
        .group_by(func.extract("month", Expense.date))
        .order_by(func.extract("month", Expense.date))
        .all()
    )
    return [(int(r.month), float(r.total)) for r in rows]


def expenses_by_category(db: Session, year: int | None = None, company_id: str = None):
    """Return list of (category, total) tuples."""
    q = db.query(Expense.category, func.sum(Expense.amount).label("total"))
    if company_id:
        q = q.filter(Expense.company_id == company_id)
    if year:
        q = q.filter(func.extract("year", Expense.date) == year)
    rows = q.group_by(Expense.category).all()
    return [(r.category, float(r.total)) for r in rows]
