"""
PPM schemas — Project, Task.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ── Project ──────────────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    budget: float = Field(default=0.0, ge=0)
    spent: float = Field(default=0.0, ge=0)
    status: str = Field(default="planning", pattern="^(planning|active|completed|delayed|on_hold)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    manager: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    end_date: Optional[date] = None
    budget: Optional[float] = Field(default=None, ge=0)
    spent: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = Field(default=None, pattern="^(planning|active|completed|delayed|on_hold)$")
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    manager: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    budget: float
    spent: float
    status: str
    priority: str
    manager: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Task ─────────────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    project_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: str = Field(default="todo", pattern="^(todo|in_progress|review|done)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(todo|in_progress|review|done)$")
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high|critical)$")
    due_date: Optional[date] = None


class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
