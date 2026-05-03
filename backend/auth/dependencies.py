import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from services.supabase_service import verify_supabase_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the current user from the Supabase JWT."""
    token = credentials.credentials
    
    # 1. Verify token via JWKS locally
    payload = verify_supabase_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    supabase_id = payload.get("sub")
    email = payload.get("email")

    # 2. Sync with local user table
    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not user:
        # Create new user on first request
        # Generate a unique company_id for the new user
        new_company_id = f"comp-{str(uuid.uuid4())[:8]}"
        user = User(
            supabase_id=supabase_id,
            email=email,
            username=email.split("@")[0],
            full_name=payload.get("user_metadata", {}).get("full_name", email.split("@")[0]),
            company_id=new_company_id,
            hashed_password="SUPABASE_AUTH",
            role="admin",  # First user of a company is admin
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def require_role(*allowed_roles: str):
    """Restricts access to users whose role is in *allowed_roles*."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized.",
            )
        return current_user
    return role_checker
