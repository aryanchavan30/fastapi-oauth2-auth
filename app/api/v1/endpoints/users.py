from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_superuser
from app.crud.user import user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Retrieve users (Admin only).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Users can only see their own profile, unless they're superuser
    if db_user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return db_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Check if username is being updated and if it's already taken
    if user_in.username and user_in.username != current_user.username:
        existing_user = user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
    
    updated_user = user.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user

@router.delete("/me")
def delete_user_me(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete own user account.
    """
    db.delete(current_user)
    db.commit()
    return {"message": "User account deleted successfully"}