from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
from typing import Optional
from uuid import UUID
import asyncpg
from src.core.database import get_db
from src.core.deps import get_current_user
from src.schemas.user import User
from src.services.book_service import BookService
from src.services.import_service import ImportService
from src.schemas.book import (
    Book,
    BookCreate,
    BookUpdate,
    BookFilters,
    BulkImportResponse,
)
from src.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate, connection: asyncpg.Connection = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new book"""
    service = BookService(connection)
    return await service.create_book(book_data)


@router.get("/", response_model=PaginatedResponse[Book])
async def get_books(
    title: Optional[str] = Query(None, description="Filter by title"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    year_from: Optional[int] = Query(None, description="Filter from year"),
    year_to: Optional[int] = Query(None, description="Filter to year"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("title", description="Sort by: title, year, author"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    connection: asyncpg.Connection = Depends(get_db),
):
    """Get books with filtering, pagination, and sorting"""
    filters = BookFilters(
        title=title, author=author, year_from=year_from, year_to=year_to
    )

    service = BookService(connection)
    return await service.get_books(filters, page, size, sort_by, sort_order)


@router.get("/{book_id}", response_model=Book)
async def get_book_by_id(
    book_id: UUID, connection: asyncpg.Connection = Depends(get_db)
):
    """Get a specific book by ID"""
    service = BookService(connection)
    return await service.get_book_by_id(book_id)


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    connection: asyncpg.Connection = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a book"""
    service = BookService(connection)
    return await service.update_book(book_id, book_data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        book_id: UUID, connection: asyncpg.Connection = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Delete a book"""
    service = BookService(connection)
    await service.delete_book(book_id)


@router.post("/import", response_model=BulkImportResponse)
async def import_books(
    file: UploadFile = File(...), connection: asyncpg.Connection = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import books from CSV or JSON file"""
    if file.content_type not in ["application/json", "text/csv"]:
        raise HTTPException(
            status_code=400, detail="Only JSON and CSV files are supported"
        )

    service = ImportService(connection)
    return await service.import_from_file(file)
