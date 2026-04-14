"""
HCM schemas — Employee, Attendance, Payroll, Performance.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime


# ── Employee ─────────────────────────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., max_length=20)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    phone: Optional[str] = None
    department: str = Field(..., max_length=50)
    position: str = Field(..., max_length=80)
    salary: float = Field(..., gt=0)
    hire_date: date
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[float] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class EmployeeOut(BaseModel):
    id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department: str
    position: str
    salary: float
    hire_date: date
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Attendance ───────────────────────────────────────────────────────────────
class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: str = Field(default="present", pattern="^(present|absent|late|leave)$")


class AttendanceUpdate(BaseModel):
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: Optional[str] = Field(default=None, pattern="^(present|absent|late|leave)$")


class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: str

    class Config:
        from_attributes = True


# ── Payroll ──────────────────────────────────────────────────────────────────
class PayrollCreate(BaseModel):
    employee_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)
    basic_salary: float = Field(..., gt=0)
    deductions: float = Field(default=0.0, ge=0)
    bonuses: float = Field(default=0.0, ge=0)
    net_salary: Optional[float] = None  # auto-calculated if omitted
    paid: bool = False


class PayrollUpdate(BaseModel):
    deductions: Optional[float] = Field(default=None, ge=0)
    bonuses: Optional[float] = Field(default=None, ge=0)
    paid: Optional[bool] = None


class PayrollOut(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    basic_salary: float
    deductions: float
    bonuses: float
    net_salary: float
    paid: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Performance ──────────────────────────────────────────────────────────────
class PerformanceCreate(BaseModel):
    employee_id: int
    quarter: int = Field(..., ge=1, le=4)
    year: int = Field(..., ge=2020)
    rating: float = Field(..., ge=1.0, le=5.0)
    goals_met: int = Field(default=0, ge=0)
    goals_total: int = Field(default=0, ge=0)
    review_notes: Optional[str] = None
    reviewer: Optional[str] = None


class PerformanceUpdate(BaseModel):
    rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    goals_met: Optional[int] = Field(default=None, ge=0)
    goals_total: Optional[int] = Field(default=None, ge=0)
    review_notes: Optional[str] = None


class PerformanceOut(BaseModel):
    id: int
    employee_id: int
    quarter: int
    year: int
    rating: float
    goals_met: int
    goals_total: int
    review_notes: Optional[str] = None
    reviewer: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
