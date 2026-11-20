from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import User, UserRole
from app.core.security import decode_access_token
from app.core.logging_config import log_admin_event

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates the Bearer JWT token from the Authorization header.
    Pins the algorithm, verifies signature and expiry, and loads user from DB.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject (sub).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Safe parameterized query via SQLAlchemy
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been deleted.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Enforces Role-Based Access Control (RBAC).
    Rejects regular customers from accessing privileged administrative routes.
    """
    if current_user.role != UserRole.ADMIN:
        log_admin_event(
            "UNAUTHORIZED_ADMIN_ROUTE_ATTEMPT",
            current_user.username,
            "JWT_Session",
            f"User with role '{current_user.role.value}' attempted to access admin route",
            status="BLOCKED",
            level="warning"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrator privileges required.",
        )
    return current_user
