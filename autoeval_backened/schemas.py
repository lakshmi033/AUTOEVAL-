# schemas.py
"""
Pydantic schemas for request and response payloads.

These are separate from SQLAlchemy models to keep API contracts
clean, documented, and decoupled from the ORM.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------
# User-related schemas
# ---------------------

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    """
    Payload for user registration.
    Role is not accepted from client to keep things simple and safe:
    all self-registered users become 'user' by default.
    Admin(s) can be created manually or via migration.
    """
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    """
    Payload for user login.
    """
    email: EmailStr
    password: str


class UserRead(UserBase):
    """
    Public representation of a user.
    """
    id: int
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 compatible with ORM objects


# ---------------------
# Auth / JWT schemas
# ---------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Internal representation of token payload used during verification.
    """
    email: Optional[str] = None
    role: Optional[str] = None