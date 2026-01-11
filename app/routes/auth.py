"""
Authentication routes for user login and session management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db import get_db
from app.models import User
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

# Simple session storage (in production, use Redis or database)
sessions = {}  # {session_token: {user_id, username, role, expires_at}}

# Security scheme
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "student"  # Default to student


class LoginResponse(BaseModel):
    session_token: str
    user: dict
    message: str


class SessionUser(BaseModel):
    user_id: int
    username: str
    role: str


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[SessionUser]:
    """Get current authenticated user from session token. Returns None if not authenticated."""
    if not credentials:
        return None
    
    token = credentials.credentials
    session_data = sessions.get(token)
    
    if not session_data:
        return None
    
    # Check if session expired
    if datetime.utcnow() > session_data["expires_at"]:
        del sessions[token]
        return None
    
    return SessionUser(
        user_id=session_data["user_id"],
        username=session_data["username"],
        role=session_data["role"]
    )


def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> SessionUser:
    """Require authentication - raises error if not authenticated."""
    user = get_current_user(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin(
    current_user: Optional[SessionUser] = Depends(get_current_user)
) -> SessionUser:
    """Get current user and verify they are an admin."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Only students can register - admin accounts are created separately."""
    # Prevent admin registration through public API
    if request.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin accounts cannot be created through registration. Please contact system administrator."
        )
    
    # Force student role for all registrations (security measure)
    user_role = "student"
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user (always as student)
    user = User(
        username=request.username,
        password_hash=User.hash_password(request.password),
        role=user_role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User registered successfully",
        "user": user.to_dict()
    }


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and create a session."""
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create session token
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hour session
    
    sessions[session_token] = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "expires_at": expires_at
    }
    
    return LoginResponse(
        session_token=session_token,
        user=user.to_dict(),
        message="Login successful"
    )


@router.post("/logout")
def logout(current_user: Optional[SessionUser] = Depends(get_current_user)):
    """Logout and invalidate session."""
    if current_user:
        # Find and remove session (we need to search by user_id since we don't have token here)
        tokens_to_remove = [
            token for token, data in sessions.items()
            if data["user_id"] == current_user.user_id
        ]
        for token in tokens_to_remove:
            del sessions[token]
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=dict)
def get_current_user_info(current_user: SessionUser = Depends(require_auth)):
    """Get current user information."""
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role
    }


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: SessionUser = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Change password for the current user."""
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify old password
    if not user.verify_password(request.old_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Update password
    user.password_hash = User.hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
