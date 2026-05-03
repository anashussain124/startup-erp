"""
HCM Router — Employee, Attendance, Payroll, Performance endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user, require_role
from schemas.hcm import (
    EmployeeCreate, EmployeeUpdate, EmployeeOut,
    AttendanceCreate, AttendanceUpdate, AttendanceOut,
    PayrollCreate, PayrollUpdate, PayrollOut,
    PerformanceCreate, PerformanceUpdate, PerformanceOut,
)
from services import hcm_service

router = APIRouter(prefix="/api", tags=["HCM"])


# ── Employees ────────────────────────────────────────────────────────────────
@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return hcm_service.create_employee(db, data, user.company_id)


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    department: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return hcm_service.get_employees(db, user.company_id, skip, limit, department)


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    emp = hcm_service.get_employee(db, employee_id, user.company_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    emp = hcm_service.update_employee(db, employee_id, data, user.company_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not hcm_service.delete_employee(db, employee_id, user.company_id):
        raise HTTPException(status_code=404, detail="Employee not found")


# ── Attendance ───────────────────────────────────────────────────────────────
@router.post("/attendance", response_model=AttendanceOut, status_code=201)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return hcm_service.create_attendance(db, data, user.company_id)


@router.get("/attendance", response_model=list[AttendanceOut])
def list_attendance(
    employee_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return hcm_service.get_attendance(db, user.company_id, employee_id, skip, limit)


@router.put("/attendance/{record_id}", response_model=AttendanceOut)
def update_attendance(
    record_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    record = hcm_service.update_attendance(db, record_id, data, user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/attendance/{record_id}", status_code=204)
def delete_attendance(
    record_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not hcm_service.delete_attendance(db, record_id, user.company_id):
        raise HTTPException(status_code=404, detail="Record not found")


# ── Payroll ──────────────────────────────────────────────────────────────────
@router.post("/payroll", response_model=PayrollOut, status_code=201)
def create_payroll(
    data: PayrollCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return hcm_service.create_payroll(db, data, user.company_id)


@router.get("/payroll", response_model=list[PayrollOut])
def list_payroll(
    employee_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return hcm_service.get_payrolls(db, user.company_id, employee_id, skip, limit)


@router.put("/payroll/{record_id}", response_model=PayrollOut)
def update_payroll(
    record_id: int,
    data: PayrollUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    record = hcm_service.update_payroll(db, record_id, data, user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/payroll/{record_id}", status_code=204)
def delete_payroll(
    record_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not hcm_service.delete_payroll(db, record_id, user.company_id):
        raise HTTPException(status_code=404, detail="Record not found")


# ── Performance ──────────────────────────────────────────────────────────────
@router.post("/performance", response_model=PerformanceOut, status_code=201)
def create_performance(
    data: PerformanceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return hcm_service.create_performance(db, data, user.company_id)


@router.get("/performance", response_model=list[PerformanceOut])
def list_performance(
    employee_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return hcm_service.get_performances(db, user.company_id, employee_id, skip, limit)


@router.put("/performance/{record_id}", response_model=PerformanceOut)
def update_performance(
    record_id: int,
    data: PerformanceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    record = hcm_service.update_performance(db, record_id, data, user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/performance/{record_id}", status_code=204)
def delete_performance(
    record_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not hcm_service.delete_performance(db, record_id, user.company_id):
        raise HTTPException(status_code=404, detail="Record not found")
