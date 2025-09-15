from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class AuthorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    biography: Optional[str] = None

    @field_validator("first_name", "last_name")
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")

        if not re.match(r"^[a-zA-Z\s\-\']+", v.strip()):
            raise ValueError(
                "Name can only contain letters, spaces, hyphens, dots, and apostrophes"
            )

        return v.strip().title()


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    biography: Optional[str] = None

    @field_validator("first_name", "last_name")
    def validate_names(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty or just whitespace")

            if not re.match(r"^[a-zA-Z\s\-\']+", v.strip()):
                raise ValueError(
                    "Name can only contain letters, spaces, hyphens, dots, and apostrophes"
                )

            return v.strip().title()
        return v


class Author(AuthorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
