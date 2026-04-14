"""
PPM Router — Project, Task endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user, require_role
from schemas.ppm import (
    ProjectCreate, ProjectUpdate, ProjectOut,
    TaskCreate, TaskUpdate, TaskOut,
)
from services import ppm_service

router = APIRouter(prefix="/api", tags=["PPM"])


# ── Projects ─────────────────────────────────────────────────────────────────
@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return ppm_service.create_project(db, data)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return ppm_service.get_projects(db, skip, limit, status)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    project = ppm_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    project = ppm_service.update_project(db, project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not ppm_service.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")


# ── Tasks ────────────────────────────────────────────────────────────────────
@router.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return ppm_service.create_task(db, data)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    project_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return ppm_service.get_tasks(db, project_id, skip, limit, status)


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = ppm_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = ppm_service.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    if not ppm_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
