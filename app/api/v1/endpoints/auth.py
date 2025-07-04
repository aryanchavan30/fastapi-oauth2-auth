from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.crud.user import user
from app.schemas.user import UserCreate, UserResponse, PasswordReset, PasswordResetConfirm
from app.schemas.token import Token, RefreshToken
from app.models.user import User
from app.utils.email import send_verification_email, send_password_reset_email

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system.",
        )
    
    existing_username = user.get_by_username(db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists in the system.",
        )
    
    # Create new user
    new_user = user.create(db, obj_in=user_in)
    
    # Send verification email in background
    if new_user.verification_token:
        background_tasks.add_task(
            send_verification_email,
            new_user.email,
            new_user.username,
            new_user.verification_token
        )
    
    return new_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    authenticated_user = user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active(authenticated_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Optional: Check if user is verified
    # if not user.is_verified(authenticated_user):
    #     raise HTTPException(status_code=400, detail="Email not verified")
    
    # Update last login
    user.update_last_login(db, authenticated_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            authenticated_user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(authenticated_user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_data: RefreshToken
) -> Any:
    """
    Refresh access token using refresh token.
    """
    user_id = verify_token(refresh_data.refresh_token, "refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    current_user = user.get(db, id=int(user_id))
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            current_user.id, expires_delta=access_token_expires
        ),
        "refresh_token": create_refresh_token(current_user.id),
        "token_type": "bearer",
    }

@router.get("/verify/{token}")
def verify_email(
    *,
    db: Session = Depends(get_db),
    token: str
) -> Any:
    """
    Verify user email with verification token.
    """
    db_user = db.query(User).filter(User.verification_token == token).first()
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )
    
    if db_user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User already verified"
        )
    
    user.verify_user(db, db_user)
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(
    *,
    db: Session = Depends(get_db),
    password_reset: PasswordReset,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Send password reset email.
    """
    db_user = user.get_by_email(db, email=password_reset.email)
    if db_user:
        # Generate reset token
        reset_token = user.create_reset_token(db, db_user)
        
        # Send password reset email in background
        background_tasks.add_task(
            send_password_reset_email,
            db_user.email,
            db_user.username,
            reset_token
        )
    
    # Always return success message for security
    return {"message": "Password reset email sent if email exists"}

@router.post("/reset-password")
def reset_password(
    *,
    db: Session = Depends(get_db),
    password_reset: PasswordResetConfirm
) -> Any:
    """
    Reset password with reset token.
    """
    db_user = user.get_by_reset_token(db, token=password_reset.token)
    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    user.reset_password(db, db_user, password_reset.new_password)
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout user (client should delete tokens).
    """
    return {"message": "Successfully logged out"}

@router.post("/resend-verification")
def resend_verification_email(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Resend verification email to current user.
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User already verified"
        )
    
    if not current_user.verification_token:
        # Generate new verification token if none exists
        import secrets
        current_user.verification_token = secrets.token_urlsafe(32)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    
    # Send verification email in background
    background_tasks.add_task(
        send_verification_email,
        current_user.email,
        current_user.username,
        current_user.verification_token
    )
    
    return {"message": "Verification email sent"}