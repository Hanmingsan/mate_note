# backend/app/db/models/user.py

from sqlalchemy import Column, Integer, String, Boolean
from .base import Base # Import Base from models/base.py

class User(Base):
    """
    User database model.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="Unique User ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="Username (unique)")
    email = Column(String, unique=True, index=True, nullable=True, comment="Email address (unique, optional)")
    hashed_password = Column(String, nullable=False, comment="Hashed password")
    full_name = Column(String(100), nullable=True, comment="User's full name")
    is_active = Column(Boolean(), default=True, comment="Is the user account active?")
    is_superuser = Column(Boolean(), default=False, comment="Is the user a superuser/admin?")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

