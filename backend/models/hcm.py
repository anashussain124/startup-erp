"""
HCM models — Employee, Attendance, Payroll, Performance.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, Time, Text,
    ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_code = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=False)
    position = Column(String(80), nullable=False)
    salary = Column(Float, nullable=False)
    hire_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    payroll_records = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")
    performance_records = relationship("Performance", back_populates="employee", cascade="all, delete-orphan")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    status = Column(String(20), nullable=False, default="present")  # present | absent | late | leave

    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        Index("ix_attendance_emp_date", "employee_id", "date"),
    )


class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(Float, nullable=False)
    deductions = Column(Float, default=0.0)
    bonuses = Column(Float, default=0.0)
    net_salary = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="payroll_records")


class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    quarter = Column(Integer, nullable=False)  # 1-4
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)  # 1.0 - 5.0
    goals_met = Column(Integer, default=0)
    goals_total = Column(Integer, default=0)
    review_notes = Column(Text, nullable=True)
    reviewer = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="performance_records")
