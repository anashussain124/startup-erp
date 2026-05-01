"""
Database engine, session factory, and base model.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, DB_TYPE

# ---------------------------------------------------------------------------
# Engine — configure based on actual database URL, not DB_TYPE
# ---------------------------------------------------------------------------
_is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 3600
    engine_kwargs["pool_pre_ping"] = True  # detect stale connections

engine = create_engine(DATABASE_URL, echo=False, **engine_kwargs)

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
