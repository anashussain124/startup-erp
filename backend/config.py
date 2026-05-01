"""
Application Configuration
Reads settings from environment variables with sensible defaults.
"""
import os


# =============================================================================
# Database Configuration
# =============================================================================
# Priority: DATABASE_URL env var > DB_TYPE-based construction
# Render provides DATABASE_URL automatically for PostgreSQL services.
DATABASE_URL_OVERRIDE = os.getenv("DATABASE_URL")

# DB_TYPE: "sqlite", "mysql", or "postgresql"
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# MySQL settings (used when DB_TYPE == "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "startup_erp")

# PostgreSQL settings (used when DB_TYPE == "postgresql")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "startup_erp")

# SQLite settings (used when DB_TYPE == "sqlite")
SQLITE_PATH = os.getenv("SQLITE_PATH", "startup_erp.db")

def get_database_url() -> str:
    """Return the appropriate database URL based on config priority."""
    # 1. Explicit DATABASE_URL takes top priority (Render, Heroku, etc.)
    if DATABASE_URL_OVERRIDE:
        return DATABASE_URL_OVERRIDE
    # 2. Construct from DB_TYPE
    if DB_TYPE == "mysql":
        return (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    if DB_TYPE == "postgresql":
        return (
            f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}"
            f"@{PG_HOST}:{PG_PORT}/{PG_DB}"
        )
    return f"sqlite:///{SQLITE_PATH}"

DATABASE_URL = get_database_url()


# =============================================================================
# JWT Configuration
# =============================================================================
JWT_SECRET = os.getenv("JWT_SECRET", "erp-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "480"))  # 8 hours


# =============================================================================
# CORS Configuration
# =============================================================================
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


# =============================================================================
# ML Models Directory
# =============================================================================
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
