"""
Finance Router — Expense, Revenue endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user, require_role
from schemas.finance import (
    ExpenseCreate, ExpenseUpdate, ExpenseOut,
    RevenueCreate, RevenueUpdate, RevenueOut,
)
from services import finance_service

router = APIRouter(prefix="/api", tags=["Finance"])


# ── Expenses ─────────────────────────────────────────────────────────────────
@router.post("/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return finance_service.create_expense(db, data)


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    category: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return finance_service.get_expenses(db, skip, limit, category)


@router.get("/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    record = finance_service.get_expense(db, expense_id)
    if not record:
        raise HTTPException(status_code=404, detail="Expense not found")
    return record


@router.put("/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    record = finance_service.update_expense(db, expense_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Expense not found")
    return record


@router.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not finance_service.delete_expense(db, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")


# ── Revenue ──────────────────────────────────────────────────────────────────
@router.post("/revenue", response_model=RevenueOut, status_code=201)
def create_revenue(
    data: RevenueCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return finance_service.create_revenue(db, data)


@router.get("/revenue", response_model=list[RevenueOut])
def list_revenue(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    source: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return finance_service.get_revenues(db, skip, limit, source)


@router.get("/revenue/{revenue_id}", response_model=RevenueOut)
def get_revenue(revenue_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    record = finance_service.get_revenue(db, revenue_id)
    if not record:
        raise HTTPException(status_code=404, detail="Revenue not found")
    return record


@router.put("/revenue/{revenue_id}", response_model=RevenueOut)
def update_revenue(
    revenue_id: int,
    data: RevenueUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    record = finance_service.update_revenue(db, revenue_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Revenue not found")
    return record


@router.delete("/revenue/{revenue_id}", status_code=204)
def delete_revenue(
    revenue_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not finance_service.delete_revenue(db, revenue_id):
        raise HTTPException(status_code=404, detail="Revenue not found")
