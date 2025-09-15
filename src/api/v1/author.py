from fastapi import APIRouter, Depends, Query, status
import asyncpg
from uuid import UUID
from src.core.database import get_db
from src.services.author_service import AuthorService
from src.schemas.author import Author, AuthorCreate, AuthorUpdate
from src.schemas.pagination import PaginatedResponse
from src.core.deps import get_current_user

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=Author, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    connection: asyncpg.Connection = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new author"""
    service = AuthorService(connection)
    return await service.create_author(author_data)


@router.get("/", response_model=PaginatedResponse[Author])
async def get_authors(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    connection: asyncpg.Connection = Depends(get_db),
):
    """Get all authors with pagination"""
    service = AuthorService(connection)
    return await service.get_authors(page, size)


@router.get("/search", response_model=PaginatedResponse[Author])
async def search_authors(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    connection: asyncpg.Connection = Depends(get_db),
):
    """Search authors by name"""
    service = AuthorService(connection)
    offset = (page - 1) * size
    authors = await service.author_repo.search(q, size, offset)
    total = await service.author_repo.connection.fetchval(
        "SELECT COUNT(*) FROM authors WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER($1)",
        f"%{q}%",
    )

    return PaginatedResponse(
        items=[Author(**author) for author in authors],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{author_id}", response_model=Author)
async def get_author_by_id(
    author_id: UUID, connection: asyncpg.Connection = Depends(get_db)
):
    """Get a specific author by ID"""
    service = AuthorService(connection)
    return await service.get_author_by_id(author_id)


@router.put("/{author_id}", response_model=Author)
async def update_author(
    author_id: UUID,
    author_data: AuthorUpdate,
    connection: asyncpg.Connection = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Update an author"""
    service = AuthorService(connection)
    return await service.update_author(author_id, author_data)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: UUID,
    connection: asyncpg.Connection = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete an author"""
    service = AuthorService(connection)
    await service.delete_author(author_id)
