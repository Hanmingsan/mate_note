# backend/app/schemas/token.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Schema for the access token response.
    """
    access_token: str
    token_type: str = "bearer" # Standard token type

class TokenData(BaseModel):
    """
    Schema for data encoded within the JWT token.
    Typically contains the username (or user ID).
    """
    username: Optional[str] = None
    # You could add other fields like user_id, scopes, etc.

