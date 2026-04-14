"""
PPM Service — business logic for Project, Task.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.ppm import Project, Task
from schemas.ppm import (
    ProjectCreate, ProjectUpdate,
    TaskCreate, TaskUpdate,
)
from datetime import datetime, timezone


# ═══════════════════════════════════════════════════════════════════════════
# Project CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_projects(db: Session, skip: int = 0, limit: int = 100, status: str | None = None):
    q = db.query(Project)
    if status:
        q = q.filter(Project.status == status)
    return q.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def update_project(db: Session, project_id: int, data: ProjectUpdate) -> Project | None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Task CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_task(db: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, project_id: int | None = None, skip: int = 0, limit: int = 100, status: str | None = None):
    q = db.query(Task)
    if project_id:
        q = q.filter(Task.project_id == project_id)
    if status:
        q = q.filter(Task.status == status)
    return q.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    updates = data.model_dump(exclude_unset=True)
    # Auto-set completed_at when task is marked done
    if updates.get("status") == "done" and task.status != "done":
        task.completed_at = datetime.now(timezone.utc)
    for key, value in updates.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# Aggregation helpers
# ═══════════════════════════════════════════════════════════════════════════
def project_stats(db: Session):
    """Return counts by project status."""
    rows = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    return {status: count for status, count in rows}


def task_completion_rate(db: Session, project_id: int) -> float:
    """Return percentage of completed tasks for a project."""
    total = db.query(Task).filter(Task.project_id == project_id).count()
    if total == 0:
        return 0.0
    done = db.query(Task).filter(Task.project_id == project_id, Task.status == "done").count()
    return round((done / total) * 100, 1)
