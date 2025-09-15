from typing import Dict, Any
from uuid import UUID
import asyncpg
from datetime import datetime, timezone
from fastapi import HTTPException, status
from src.repositories.book import BookRepository
from src.repositories.author import AuthorRepository
from src.schemas.book import BookCreate, BookUpdate, BookFilters, Book
from src.schemas.pagination import PaginatedResponse


class BookService:
    def __init__(self, connection: asyncpg.Connection):
        self.book_repo = BookRepository(connection)
        self.author_repo = AuthorRepository(connection)

    async def create_book(self, book_data: BookCreate) -> Book:
        if book_data.author_id:
            author = await self.author_repo.get_by_id(book_data.author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Author with id {book_data.author_id} not found",
                )

        book = await self.book_repo.create(book_data)
        return await self._format_book_response(book)

    async def get_book_by_id(self, book_id: UUID) -> Book:
        book = await self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )
        return await self._format_book_response(book)

    async def get_books(
        self,
        filters: BookFilters,
        page: int = 1,
        size: int = 20,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> PaginatedResponse[Book]:
        offset = (page - 1) * size

        books = await self.book_repo.get_all(filters, size, offset, sort_by, sort_order)
        total = await self.book_repo.get_total_count(filters)

        formatted_books = [await self._format_book_response(book) for book in books]

        return PaginatedResponse(
            items=formatted_books, total=total, page=page, size=size
        )

    async def update_book(self, book_id: UUID, book_data: BookUpdate) -> Book:
        existing = await self.book_repo.get_by_id(book_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )

        if book_data.author_id:
            author = await self.author_repo.get_by_id(book_data.author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Author with id {book_data.author_id} not found",
                )

        updated_book = await self.book_repo.update(book_id, book_data)
        return await self._format_book_response(updated_book)

    async def delete_book(self, book_id: UUID) -> bool:
        existing = await self.book_repo.get_by_id(book_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )

        return await self.book_repo.delete(book_id)

    async def _format_book_response(self, book_data: Dict[str, Any]) -> Book:
        """Format book data with author"""
        author = None
        if book_data.get("author_id"):
            author = await self.author_repo.get_by_id(book_data["author_id"])

        return Book(
            id=book_data["id"],
            title=book_data["title"],
            content=book_data["content"],
            description=book_data["description"],
            published_year=int(book_data["published_year"]),
            genre=book_data["genre"],
            author=author,
            created_at=book_data.get("created_at", datetime.now(timezone.utc)),
            updated_at=book_data.get("updated_at", datetime.now(timezone.utc))
        )
