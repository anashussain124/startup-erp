"""
FastAPI Application — Startup ERP System
Main entry point. Registers all routers and configures middleware.
"""
import sys
import os

# Add backend dir to path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from config import CORS_ORIGINS
from database import engine, Base, SessionLocal

# Import all models so metadata knows about them
import models  # noqa

# Routers
from auth.router import router as auth_router
from routers.hcm import router as hcm_router
from routers.finance import router as finance_router
from routers.procurement import router as procurement_router
from routers.ppm import router as ppm_router
from routers.crm import router as crm_router
from routers.dashboard import router as dashboard_router
from routers.reports import router as reports_router
from ml.predict import router as ml_router

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Startup ERP System",
    description="ML-Enabled Enterprise Resource Planning platform for startups",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create Tables ────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ── Auto-seed on first deploy ────────────────────────────────────────────────
@app.on_event("startup")
def seed_on_first_run():
    """Seed demo data if the database is empty (first deploy)."""
    db = SessionLocal()
    try:
        user_count = db.query(models.user.User).count()
        if user_count == 0:
            print("⚡ Empty database detected — seeding demo data...")
            from seed_data import seed
            seed()
            print("✅ Demo data seeded successfully!")
    except Exception as e:
        print(f"⚠ Seed check skipped: {e}")
    finally:
        db.close()


# ── Register Routers (BEFORE static mount) ───────────────────────────────────
app.include_router(auth_router)
app.include_router(hcm_router)
app.include_router(finance_router)
app.include_router(procurement_router)
app.include_router(ppm_router)
app.include_router(crm_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(ml_router)


@app.get("/")
def root():
    """Redirect to the frontend login page."""
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/info")
def api_info():
    return {
        "name": "Startup ERP System",
        "version": "1.0.0",
        "docs": "/docs",
        "modules": ["HCM", "Finance", "Procurement", "PPM", "CRM", "ML"],
    }


# ── Mount Frontend (AFTER routers so API routes aren't shadowed) ─────────────
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
