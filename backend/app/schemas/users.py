# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# --- Base User Schema ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)

# --- Schema for User Creation ---
class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Plain password during creation

# --- Schema for User Update (Example) ---
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8) # Allow password update
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# --- Schema for Reading User Data (API Response) ---
# Excludes sensitive info like hashed_password
class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True # Pydantic V2

# --- Schema for User in DB (includes hashed password) ---
# Useful internally but not exposed via API
class UserInDB(User):
    hashed_password: str

