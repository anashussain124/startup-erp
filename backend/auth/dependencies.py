"""
FastAPI dependencies for authentication and role-based access control.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.jwt_handler import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from the Bearer token."""
    token = credentials.credentials
    
    # 1. Try local JWT first (for backward compatibility/local testing)
    payload = decode_token(token)
    if payload:
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user

    # 2. Try Supabase Auth
    from services.supabase_service import verify_supabase_token
    sb_user = verify_supabase_token(token)
    if sb_user:
        # Sync with local user table using supabase_id
        user = db.query(User).filter(User.supabase_id == sb_user.id).first()
        if not user:
            # Auto-create local user if it doesn't exist
            # For multi-company, we assume company_id is in metadata or email domain
            company_id = sb_user.user_metadata.get("company_id", "default") if sb_user.user_metadata else "default"
            user = User(
                supabase_id=sb_user.id,
                email=sb_user.email,
                username=sb_user.email.split("@")[0],
                full_name=sb_user.user_metadata.get("full_name", "") if sb_user.user_metadata else "",
                company_id=company_id,
                hashed_password="SUPABASE_AUTH", # Password managed by Supabase
                role=sb_user.user_metadata.get("role", "employee") if sb_user.user_metadata else "employee"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
    )


def require_role(*allowed_roles: str):
    """
    Dependency factory — restricts access to users whose role is in *allowed_roles*.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}",
            )
        return current_user
    return role_checker
