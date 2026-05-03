"""
HCM Service — business logic for Employee, Attendance, Payroll, Performance.
"""
from sqlalchemy.orm import Session
from models.hcm import Employee, Attendance, Payroll, Performance
from schemas.hcm import (
    EmployeeCreate, EmployeeUpdate,
    AttendanceCreate, AttendanceUpdate,
    PayrollCreate, PayrollUpdate,
    PerformanceCreate, PerformanceUpdate,
)


# ═══════════════════════════════════════════════════════════════════════════
# Employee CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_employee(db: Session, data: EmployeeCreate, company_id: str) -> Employee:
    # Duplicate checks within company
    if db.query(Employee).filter(Employee.employee_code == data.employee_code, Employee.company_id == company_id).first():
        raise ValueError(f"Employee code '{data.employee_code}' already exists")
    if db.query(Employee).filter(Employee.email == data.email, Employee.company_id == company_id).first():
        raise ValueError(f"Email '{data.email}' already exists")
    emp = Employee(**data.model_dump(), company_id=company_id)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def get_employees(db: Session, company_id: str, skip: int = 0, limit: int = 100, department: str | None = None):
    q = db.query(Employee).filter(Employee.company_id == company_id)
    if department:
        q = q.filter(Employee.department == department)
    return q.offset(skip).limit(limit).all()


def get_employee(db: Session, employee_id: int, company_id: str) -> Employee | None:
    return db.query(Employee).filter(Employee.id == employee_id, Employee.company_id == company_id).first()


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate, company_id: str) -> Employee | None:
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.company_id == company_id).first()
    if not emp:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


def delete_employee(db: Session, employee_id: int, company_id: str) -> bool:
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.company_id == company_id).first()
    if not emp:
        return False
    db.delete(emp)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Attendance CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_attendance(db: Session, data: AttendanceCreate, company_id: str) -> Attendance:
    record = Attendance(**data.model_dump(), company_id=company_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_attendance(db: Session, company_id: str, employee_id: int | None = None, skip: int = 0, limit: int = 100):
    q = db.query(Attendance).filter(Attendance.company_id == company_id)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    return q.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()


def update_attendance(db: Session, record_id: int, data: AttendanceUpdate, company_id: str) -> Attendance | None:
    record = db.query(Attendance).filter(Attendance.id == record_id, Attendance.company_id == company_id).first()
    if not record:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_attendance(db: Session, record_id: int, company_id: str) -> bool:
    record = db.query(Attendance).filter(Attendance.id == record_id, Attendance.company_id == company_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Payroll CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_payroll(db: Session, data: PayrollCreate, company_id: str) -> Payroll:
    d = data.model_dump()
    if d.get("net_salary") is None:
        d["net_salary"] = d["basic_salary"] - d["deductions"] + d["bonuses"]
    record = Payroll(**d, company_id=company_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_payrolls(db: Session, company_id: str, employee_id: int | None = None, skip: int = 0, limit: int = 100):
    q = db.query(Payroll).filter(Payroll.company_id == company_id)
    if employee_id:
        q = q.filter(Payroll.employee_id == employee_id)
    return q.order_by(Payroll.year.desc(), Payroll.month.desc()).offset(skip).limit(limit).all()


def update_payroll(db: Session, record_id: int, data: PayrollUpdate, company_id: str) -> Payroll | None:
    record = db.query(Payroll).filter(Payroll.id == record_id, Payroll.company_id == company_id).first()
    if not record:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.net_salary = record.basic_salary - record.deductions + record.bonuses
    db.commit()
    db.refresh(record)
    return record


def delete_payroll(db: Session, record_id: int, company_id: str) -> bool:
    record = db.query(Payroll).filter(Payroll.id == record_id, Payroll.company_id == company_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Performance CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_performance(db: Session, data: PerformanceCreate, company_id: str) -> Performance:
    record = Performance(**data.model_dump(), company_id=company_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_performances(db: Session, company_id: str, employee_id: int | None = None, skip: int = 0, limit: int = 100):
    q = db.query(Performance).filter(Performance.company_id == company_id)
    if employee_id:
        q = q.filter(Performance.employee_id == employee_id)
    return q.order_by(Performance.year.desc(), Performance.quarter.desc()).offset(skip).limit(limit).all()


def update_performance(db: Session, record_id: int, data: PerformanceUpdate, company_id: str) -> Performance | None:
    record = db.query(Performance).filter(Performance.id == record_id, Performance.company_id == company_id).first()
    if not record:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_performance(db: Session, record_id: int, company_id: str) -> bool:
    record = db.query(Performance).filter(Performance.id == record_id, Performance.company_id == company_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
