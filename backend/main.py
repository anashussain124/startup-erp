"""
FastAPI Application — Startup ERP System
Main entry point. Registers all routers and configures middleware.
"""
import sys
import os
import logging
from contextlib import asynccontextmanager

# Add backend dir to path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

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
from routers.insights import router as insights_router
from routers.forecast import router as forecast_router
from routers.documents import router as documents_router
from routers.ai import router as ai_router
from routers.billing import router as billing_router


# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("erp")


# ── Lifespan (replaces deprecated @app.on_event) ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed demo data. Shutdown: cleanup."""
    # Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from seed_data import seed
        # Pass fast_seed=True if on Vercel to prevent timeouts
        seed(fast_seed=os.getenv("VERCEL") is not None)
        logger.info("[DB] Database and demo accounts verified.")
    except Exception as e:
        logger.warning(f"Seed check skipped: {e}")
    finally:
        db.close()
    # Pre-load ML models (skipped on Vercel to prevent cold-start timeouts)
    if not os.getenv("VERCEL"):
        try:
            from ml.predict import preload_models
            preload_models()
        except Exception as e:
            logger.warning(f"ML preload skipped: {e}")
    yield
    # Shutdown
    logger.info("[SHUTDOWN] Application shutting down")


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Startup ERP System",
    description="ML-Enabled Enterprise Resource Planning platform for startups",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Global Exception Handlers ───────────────────────────────────────────────
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Convert service-layer ValueError (duplicates, validation) to 409."""
    logger.warning(f"Conflict: {exc} | path={request.url.path}")
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return structured JSON."""
    logger.error(f"Unhandled error: {type(exc).__name__}: {exc} | path={request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register Routers (BEFORE static mount) ───────────────────────────────────
app.include_router(auth_router, prefix="/api")
app.include_router(hcm_router, prefix="/api")
app.include_router(finance_router, prefix="/api")
app.include_router(procurement_router, prefix="/api")
app.include_router(ppm_router, prefix="/api")
app.include_router(crm_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(ml_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(forecast_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(insights_router, prefix="/api")


@app.get("/")
def root():
    """Redirect to the frontend login page."""
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health():
    """Health check with DB connectivity test."""
    try:
        db = SessionLocal()
        db.execute(models.user.User.__table__.select().limit(1))
        db.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "healthy", "database": db_status, "version": "1.0.0"}


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
