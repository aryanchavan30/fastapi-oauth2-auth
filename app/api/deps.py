from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.crud.user import user
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token, "access")
    if user_id is None:
        raise credentials_exception
    
    current_user = user.get(db, id=int(user_id))
    if current_user is None:
        raise credentials_exception
    
    return current_user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not user.is_verified(current_user):
        raise HTTPException(status_code=400, detail="User not verified")
    return current_user

def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user