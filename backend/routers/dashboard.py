"""
Dashboard Router — KPI metrics and chart data aggregation.
Includes a simple TTL cache for KPI queries to avoid redundant DB hits.
"""
import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth.dependencies import get_current_user
from models.hcm import Employee, Attendance, Performance
from models.finance import Expense, Revenue
from models.procurement import Vendor, PurchaseOrder, InventoryItem
from models.ppm import Project, Task
from models.crm import Customer, Lead, Sale
from services import finance_service, ppm_service, crm_service
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# ── Simple TTL Cache ─────────────────────────────────────────────────────────
_kpi_cache = {"data": None, "expires": 0}
KPI_CACHE_TTL = 60  # seconds


def _get_cached_kpis():
    if _kpi_cache["data"] and time.time() < _kpi_cache["expires"]:
        return _kpi_cache["data"]
    return None


def _set_cached_kpis(data):
    _kpi_cache["data"] = data
    _kpi_cache["expires"] = time.time() + KPI_CACHE_TTL


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return key performance indicators across all modules (cached 60s)."""
    # For now, disable cache for multi-tenancy unless cache is keyed by company_id
    # cached = _get_cached_kpis()
    # if cached: return cached

    cid = user.company_id
    current_year = date.today().year

    # HCM
    total_employees = db.query(Employee).filter(Employee.company_id == cid, Employee.is_active == True).count()
    avg_performance = db.query(func.avg(Performance.rating)).filter(Performance.company_id == cid, Performance.year == current_year).scalar() or 0

    # Finance
    total_rev = finance_service.total_revenue(db, current_year, cid)
    total_exp = finance_service.total_expenses(db, current_year, cid)
    profit = total_rev - total_exp

    # Procurement
    pending_pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == cid, PurchaseOrder.status == "pending").count()
    low_stock_items = db.query(InventoryItem).filter(InventoryItem.company_id == cid, InventoryItem.quantity <= InventoryItem.reorder_level).count()

    # PPM
    active_projects = db.query(Project).filter(Project.company_id == cid, Project.status == "active").count()
    delayed_projects = db.query(Project).filter(Project.company_id == cid, Project.status == "delayed").count()

    # CRM
    total_customers = db.query(Customer).filter(Customer.company_id == cid, Customer.is_active == 1).count()
    total_leads = db.query(Lead).filter(Lead.company_id == cid).count()
    converted_leads = db.query(Lead).filter(Lead.company_id == cid, Lead.status == "converted").count()
    conversion_rate = round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0

    # Documents
    from models.document import CompanyDocument
    doc_count = db.query(CompanyDocument).filter(CompanyDocument.company_id == cid).count()

    result = {
        "hcm": {"total_employees": total_employees, "avg_performance": round(float(avg_performance), 2)},
        "finance": {"total_revenue": round(total_rev, 2), "total_expenses": round(total_exp, 2), "profit": round(profit, 2)},
        "procurement": {"pending_purchase_orders": pending_pos, "low_stock_alerts": low_stock_items},
        "ppm": {"active_projects": active_projects, "delayed_projects": delayed_projects},
        "crm": {"total_customers": total_customers, "total_leads": total_leads, "conversion_rate": conversion_rate},
        "documents": {"count": doc_count}
    }
    return result


@router.get("/charts/revenue-trend")
def revenue_trend(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Monthly revenue data for line chart."""
    yr = year or date.today().year
    data = finance_service.monthly_revenue(db, yr, user.company_id)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    values = [0.0] * 12
    for month_num, total in data:
        values[month_num - 1] = total
    return {"labels": months, "data": values}


@router.get("/charts/expense-trend")
def expense_trend(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Monthly expense data for line chart."""
    yr = year or date.today().year
    data = finance_service.monthly_expenses(db, yr, user.company_id)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    values = [0.0] * 12
    for month_num, total in data:
        values[month_num - 1] = total
    return {"labels": months, "data": values}


@router.get("/charts/expenses-by-category")
def expenses_by_category(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Expense breakdown by category for doughnut chart."""
    yr = year or date.today().year
    data = finance_service.expenses_by_category(db, yr, user.company_id)
    return {"labels": [d[0] for d in data], "data": [d[1] for d in data]}


@router.get("/charts/project-status")
def project_status_chart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Project counts by status for bar chart."""
    stats = ppm_service.project_stats(db, user.company_id)
    statuses = ["planning", "active", "completed", "delayed", "on_hold"]
    return {
        "labels": statuses,
        "data": [stats.get(s, 0) for s in statuses],
    }


@router.get("/charts/lead-pipeline")
def lead_pipeline_chart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Lead counts by status for funnel/bar chart."""
    pipeline = crm_service.lead_pipeline(db, user.company_id)
    statuses = ["new", "contacted", "qualified", "proposal", "converted", "lost"]
    return {
        "labels": statuses,
        "data": [pipeline.get(s, 0) for s in statuses],
    }


@router.get("/charts/department-headcount")
def department_headcount(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Employee count per department for bar chart."""
    rows = (
        db.query(Employee.department, func.count(Employee.id))
        .filter(Employee.company_id == user.company_id, Employee.is_active == True)
        .group_by(Employee.department)
        .all()
    )
    return {"labels": [r[0] for r in rows], "data": [r[1] for r in rows]}
