from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.models.entities import User, UserRole
from app.schemas.dto import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account"
)
def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user with bcrypt password hashing."""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )

    # Force role to customer on self-registration (Defense against Privilege Escalation)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=UserRole.CUSTOMER,
        full_name=request.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
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
    user = db.query(User).filter(User.username == user_req.username).first()
    if not user or not verify_password(user_req.password, user.hashed_password):
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
    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": user
    }
