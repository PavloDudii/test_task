from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: bool = True

    @field_validator("username")
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")

        if not re.match(r"^[a-zA-Z0-9_-]+", v.strip()):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return v.strip().lower()


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    username: Optional[str] = None
