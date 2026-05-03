import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# Database Configuration
# =============================================================================
# Priority: DATABASE_URL > POSTGRES_URL > SUPABASE_DB_URL
DATABASE_URL_OVERRIDE = (
    os.getenv("DATABASE_URL") or 
    os.getenv("POSTGRES_URL") or 
    os.getenv("SUPABASE_DB_URL")
)

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

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, quote_plus

def get_database_url() -> str:
    """Return the appropriate database URL based on config priority."""
    # 1. Explicit DATABASE_URL takes top priority (Supabase, Render, Heroku, etc.)
    if DATABASE_URL_OVERRIDE:
        url = DATABASE_URL_OVERRIDE
        
        # Standardize scheme for SQLAlchemy + Psycopg2
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            
        # Sanitize query parameters (remove 'supa' or other invalid options)
        try:
            parsed = urlparse(url)
            if parsed.query:
                query = parse_qs(parsed.query)
                # Remove known problematic parameters
                for bad_key in ['supa', 'connect_timeout']:
                    if bad_key in query:
                        query.pop(bad_key)
                
                new_query = urlencode(query, doseq=True)
                url = urlunparse(parsed._replace(query=new_query))
        except Exception:
            pass # Keep original if parsing fails
            
        return url
    
    # 2. Construct from DB_TYPE
    if DB_TYPE == "mysql":
        return (
            f"mysql+pymysql://{quote_plus(MYSQL_USER)}:{quote_plus(MYSQL_PASSWORD)}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    if DB_TYPE == "postgresql":
        return (
            f"postgresql+psycopg2://{quote_plus(PG_USER)}:{quote_plus(PG_PASSWORD)}"
            f"@{PG_HOST}:{PG_PORT}/{PG_DB}"
        )
    
    # 3. SQLite - use /tmp on Vercel because the root filesystem is read-only
    path = SQLITE_PATH
    if os.getenv("VERCEL"):
        path = f"/tmp/{SQLITE_PATH}"
    
    return f"sqlite:///{path}"

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
# Supabase Configuration
# =============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
JWKS_CACHE_TTL = int(os.getenv("JWKS_CACHE_TTL", "600"))  # 10 minutes

# =============================================================================
# OpenAI Configuration
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =============================================================================
# ML Models Directory
# =============================================================================
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
