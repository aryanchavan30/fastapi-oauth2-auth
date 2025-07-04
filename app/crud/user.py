from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser:
    def get(self, db: Session, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(self, db: Session, identifier: str) -> Optional[User]:
        return db.query(User).filter(
            or_(User.email == identifier, User.username == identifier)
        ).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        verification_token = secrets.token_urlsafe(32)
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            hashed_password=get_password_hash(obj_in.password),
            verification_token=verification_token
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_verified(self, user: User) -> bool:
        return user.is_verified

    def verify_user(self, db: Session, user: User) -> User:
        user.is_verified = True
        user.verification_token = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_reset_token(self, db: Session, user: User) -> str:
        reset_token = secrets.token_urlsafe(32)
        user.reset_password_token = reset_token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        db.add(user)
        db.commit()
        return reset_token

    def get_by_reset_token(self, db: Session, token: str) -> Optional[User]:
        return db.query(User).filter(
            User.reset_password_token == token,
            User.reset_password_expires > datetime.utcnow()
        ).first()

    def reset_password(self, db: Session, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, user: User) -> User:
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

user = CRUDUser()