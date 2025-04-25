# backend/app/db/crud/crud_user.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.db import models
from app.schemas import user as user_schemas
from app.core.security import get_password_hash # Import password hashing function

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    stmt = select(models.User).where(models.User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    stmt = select(models.User).where(models.User.username == username)
    return db.execute(stmt).scalar_one_or_none()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    stmt = select(models.User).where(models.User.email == email)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, user: user_schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
        # is_active and is_superuser default to True/False in the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Add update_user and other necessary CRUD functions as needed

