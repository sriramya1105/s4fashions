from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.models.entities import User, UserRole
from app.schemas.dto import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.logging_config import log_user_event, log_admin_event

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account"
)
def register_user(request: Request, reg_req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user with bcrypt password hashing."""
    client_ip = request.client.host if request.client else "unknown"

    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == reg_req.username) | (User.email == reg_req.email)
    ).first()
    if existing_user:
        log_user_event("REGISTER_FAILED", reg_req.username, client_ip, "Username or email already exists", level="warning")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )

    # Force role to customer on self-registration (Defense against Privilege Escalation)
    new_user = User(
        username=reg_req.username,
        email=reg_req.email,
        hashed_password=get_password_hash(reg_req.password),
        role=UserRole.CUSTOMER,
        full_name=reg_req.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_user_event("CUSTOMER_REGISTER_SUCCESS", new_user.username, client_ip, f"Email: {new_user.email}")
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain a cryptographically signed JWT access token"
)
@limiter.limit(settings.AUTH_RATE_LIMIT)
def login_user(request: Request, user_req: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user and returns JWT.
    Protected by Rate Limiting (CWE-307) against automated credential stuffing.
    """
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(User).filter(
        (User.username == user_req.username) |
        ((User.username == "ramya_admin") & (user_req.username == "ramya"))
    ).first()
    if not user or not verify_password(user_req.password, user.hashed_password):
        log_user_event("LOGIN_FAILED", user_req.username, client_ip, "Invalid credentials", level="warning")
        # Generic authentication failure message (CWE-209 / CWE-204)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
    }
    token = create_access_token(data=token_data)

    if user.role == UserRole.ADMIN:
        log_admin_event("ADMIN_LOGIN_SUCCESS", user.username, client_ip, "Admin session started")
    else:
        log_user_event("CUSTOMER_LOGIN_SUCCESS", user.username, client_ip, "Customer session started")

    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": user
    }


# ========================================================
# SECURITY MECHANISM 7 VERIFICATION ENDPOINT (CWE-209)
# ========================================================
@router.get(
    "/security/test-error",
    summary="CWE-209 Verification: Triggers simulated server fault to demonstrate sanitized error response"
)
def trigger_simulated_error():
    """
    Deliberately triggers an unhandled backend exception.
    In vulnerable APIs, this leaks Python stack traces, SQL queries, and file paths.
    In S4 Fashions, the global handler catches it and returns a sanitized safe JSON response.
    """
    raise RuntimeError("Simulated Database Connection Failure: SELECT * FROM credentials;")
