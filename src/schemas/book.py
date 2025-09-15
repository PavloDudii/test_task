from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .author import Author
import re


class Genre(str, Enum):
    fiction = "Fiction"
    nonfiction = "Non-Fiction"
    mystery = "Mystery"
    fantasy = "Fantasy"
    biography = "Biography"
    science_fiction = "Science Fiction"
    romance = "Romance"
    thriller = "Thriller"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)
    description: Optional[str] = None
    published_year: int = Field(..., ge=1800, le=datetime.now().year)
    genre: Genre

    @field_validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or just whitespace")

        cleaned_title = v.strip()
        if not re.search(r"[a-zA-Z0-9]", cleaned_title):
            raise ValueError("Title must contain at least one alphanumeric character")

        return cleaned_title

    @field_validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty or just whitespace")

        cleaned_content = v.strip()
        if len(cleaned_content) < 10:
            raise ValueError("Content must be at least 10 characters long")

        return cleaned_content

    @field_validator("published_year")
    def validate_published_year(cls, v):
        current_year = datetime.now().year
        if v < 1800:
            raise ValueError("Published year cannot be before 1800")
        if v > current_year:
            raise ValueError(
                f"Published year cannot be in the future (current year: {current_year})"
            )
        return v


class BookCreate(BookBase):
    author_id: Optional[UUID] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    description: Optional[str] = None
    published_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    genre: Optional[Genre] = None
    author_id: Optional[UUID] = None

    @field_validator("title")
    def validate_title(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty or just whitespace")

            cleaned_title = v.strip()
            if not re.search(r"[a-zA-Z0-9]", cleaned_title):
                raise ValueError(
                    "Title must contain at least one alphanumeric character"
                )

            return cleaned_title
        return v

    @field_validator("content")
    def validate_content(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Content cannot be empty or just whitespace")

            cleaned_content = v.strip()
            if len(cleaned_content) < 10:
                raise ValueError("Content must be at least 10 characters long")

            return cleaned_content
        return v

    @field_validator("published_year")
    def validate_published_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1800:
                raise ValueError("Published year cannot be before 1800")
            if v > current_year:
                raise ValueError(
                    f"Published year cannot be in the future (current year: {current_year})"
                )
        return v


class Book(BookBase):
    id: UUID
    author: Optional[Author] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookFilters(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[Genre] = None
    year_from: Optional[int] = Field(None, ge=1800, le=datetime.now().year)
    year_to: Optional[int] = Field(None, ge=1800, le=datetime.now().year)

    @field_validator("year_to")
    def validate_year_range(cls, v, values):
        if v and "year_from" in values and values["year_from"]:
            if v < values["year_from"]:
                raise ValueError("year_to must be greater than or equal to year_from")
        return v


class BulkImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = []
