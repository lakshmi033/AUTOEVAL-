# schemas.py
"""
Pydantic schemas for request and response payloads.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ---------------------
# User-related schemas
# ---------------------

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(pattern="^(teacher|student)$") # Strict role validation

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(pattern="^(teacher|student)$")
    roll_number: Optional[str] = None
    department: Optional[str] = None
    full_name: Optional[str] = None
    classroom_id: Optional[int] = None  # New field for class selection

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------
# Auth / JWT schemas
# ---------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    full_name: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# ---------------------
# Classroom schemas
# ---------------------

class ClassroomBase(BaseModel):
    name: str

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomRead(ClassroomBase):
    id: int
    teacher_id: int
    created_at: datetime
    
    # Optional: include student count if needed by frontend
    student_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ---------------------
# Enrollment / Student Profile
# ---------------------

class StudentProfileRead(UserRead):
    """ Used when listing students in a class """
    pass