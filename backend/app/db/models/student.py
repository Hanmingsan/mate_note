# backend/app/db/models/student.py

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func # For setting default timestamp
#from sqlalchemy.orm import declarative_base

# Create the base class for all models (Declarative Base)
# Recommended to put Base in a separate file (e.g., base.py) and import here
from .base import Base
# But defining it here for simplicity first
# Base = declarative_base()

class Student(Base):
    """
    Student/Teacher database model (corresponds to the 'students' table)
    """
    __tablename__ = "students" # Define table name

    id = Column(Integer, primary_key=True, index=True, comment="Unique ID") # Primary key, automatically indexed
    name = Column(String(100), nullable=False, index=True, comment="Name") # Name, cannot be null, indexed for query optimization
    email = Column(String, unique=True, index=True, nullable=True, comment="Email address (unique)") # Email, unique, indexed, nullable
    phone = Column(String(20), nullable=True, comment="Phone number") # Phone, nullable
    address = Column(String(255), nullable=True, comment="Address") # Address, nullable
    wechat = Column(String(100), nullable=True, comment="WeChat ID") # WeChat, nullable
    qq = Column(String(20), nullable=True, comment="QQ number") # QQ, nullable
    position = Column(String(50), nullable=True, index=True, comment="Position") # Position, nullable, indexed
    comments = Column(Text, nullable=True, comment="Remarks or comments") # Remarks, use Text for longer content, nullable
    avatar_url = Column(String, nullable=True, comment="URL of the avatar file") # Avatar URL, nullable

    # Automatically set creation timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="Creation timestamp"
    )
    # (Optional) Automatically set update timestamp
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="Update timestamp")

    # __repr__ method for easy debugging when printing the object
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}')>"


