import time
import requests
from jose import jwt, JWTError
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, JWKS_CACHE_TTL

# Initialize Supabase Admin Client
supabase: Client = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"[Supabase] Initialization failed: {e}")

# JWKS Cache
_jwks_cache = {"keys": None, "expires": 0}

def get_jwks():
    """Fetch JWKS from Supabase and cache it."""
    now = time.time()
    if _jwks_cache["keys"] and now < _jwks_cache["expires"]:
        return _jwks_cache["keys"]

    try:
        url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        keys = resp.json().get("keys", [])
        _jwks_cache["keys"] = keys
        _jwks_cache["expires"] = now + JWKS_CACHE_TTL
        return keys
    except Exception as e:
        print(f"[Supabase] JWKS Fetch Error: {e}")
        return []

def verify_supabase_token(token: str):
    """
    Verify a Supabase JWT token locally using JWKS and RS256.
    """
    if not SUPABASE_URL:
        return None

    try:
        # 1. Decode header to find 'kid'
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            return None

        # 2. Get JWKS and find matching key
        jwks = get_jwks()
        key = next((k for k in jwks if k["kid"] == kid), None)
        if not key:
            return None

        # 3. Verify JWT
        # Supabase JWTs are signed with RS256. Audience is 'authenticated'.
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience="authenticated",
            options={"verify_aud": True}
        )
        return payload  # Returns the decoded payload (sub, email, etc.)
    except JWTError as e:
        print(f"JWT Verification Error: {e}")
        return None
    except Exception as e:
        print(f"Token Processing Error: {e}")
        return None

def upload_to_supabase(bucket: str, path: str, file_content: bytes):
    """Upload a file to Supabase Storage."""
    if not supabase: return None
    try:
        res = supabase.storage.from_(bucket).upload(path, file_content)
        return res
    except Exception as e:
        print(f"Supabase Storage Error: {e}")
        return None

def get_public_url(bucket: str, path: str):
    """Get public URL for a file in Supabase Storage."""
    if not supabase: return ""
    return supabase.storage.from_(bucket).get_public_url(path)
