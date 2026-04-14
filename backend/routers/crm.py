"""
CRM Router — Customer, Lead, Sale endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user, require_role
from schemas.crm import (
    CustomerCreate, CustomerUpdate, CustomerOut,
    LeadCreate, LeadUpdate, LeadOut,
    SaleCreate, SaleUpdate, SaleOut,
)
from services import crm_service

router = APIRouter(prefix="/api", tags=["CRM"])


# ── Customers ────────────────────────────────────────────────────────────────
@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return crm_service.create_customer(db, data)


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    segment: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crm_service.get_customers(db, skip, limit, segment)


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    customer = crm_service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    customer = crm_service.update_customer(db, customer_id, data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not crm_service.delete_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")


# ── Leads ────────────────────────────────────────────────────────────────────
@router.post("/leads", response_model=LeadOut, status_code=201)
def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return crm_service.create_lead(db, data)


@router.get("/leads", response_model=list[LeadOut])
def list_leads(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crm_service.get_leads(db, skip, limit, status)


@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lead = crm_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/leads/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    lead = crm_service.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/leads/{lead_id}", status_code=204)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not crm_service.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")


# ── Sales ────────────────────────────────────────────────────────────────────
@router.post("/sales", response_model=SaleOut, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return crm_service.create_sale(db, data)


@router.get("/sales", response_model=list[SaleOut])
def list_sales(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    customer_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return crm_service.get_sales(db, skip, limit, customer_id)


@router.get("/sales/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sale = crm_service.get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.put("/sales/{sale_id}", response_model=SaleOut)
def update_sale(
    sale_id: int,
    data: SaleUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    sale = crm_service.update_sale(db, sale_id, data)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.delete("/sales/{sale_id}", status_code=204)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not crm_service.delete_sale(db, sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")
