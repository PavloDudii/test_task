import csv
import json
import io
from uuid import UUID
import asyncpg
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile
from src.repositories.book import BookRepository
from src.repositories.author import AuthorRepository
from src.schemas.book import BulkImportResponse, BookCreate
from src.schemas.author import AuthorCreate


class ImportService:
    def __init__(self, connection: asyncpg.Connection):
        self.book_repo = BookRepository(connection)
        self.author_repo = AuthorRepository(connection)
        self.connection = connection

    async def import_from_file(self, file: UploadFile) -> BulkImportResponse:
        content = await file.read()

        if file.content_type == "application/json":
            books_data = self._parse_json(content)
        elif file.content_type == "text/csv":
            books_data = self._parse_csv(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return await self._bulk_import_books(books_data)

    def _parse_json(self, content: bytes) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content.decode("utf-8"))
            return data if isinstance(data, list) else data.get("books", [])
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    def _parse_csv(self, content: bytes) -> List[Dict[str, Any]]:
        try:
            csv_content = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_content))
            return [dict(row) for row in reader]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV parsing error: {e}")

    async def _bulk_import_books(
            self, books_data: List[Dict[str, Any]]
    ) -> BulkImportResponse:
        success_count = 0
        error_count = 0
        errors = []

        async with self.connection.transaction():
            for i, book_data in enumerate(books_data):
                try:
                    author_id = book_data.get("author_id")
                    if not author_id and book_data.get("author"):
                        author_id = await self._get_or_create_author(book_data["author"])

                    genre = book_data.get("genre")
                    if genre:
                        genre = genre.strip()

                    book_create = BookCreate(
                        title=book_data["title"],
                        content=book_data.get("content", "No content provided"),
                        description=book_data.get("description"),
                        published_year=int(book_data.get("published_year")),
                        genre=genre,
                        author_id=author_id,
                    )

                    await self.book_repo.create(book_create)
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {i + 1}: {str(e)}")

        return BulkImportResponse(
            success_count=success_count, error_count=error_count, errors=errors
        )

    async def _get_or_create_author(self, author_name: str) -> UUID:
        """Get existing author or create new one"""
        name_parts = author_name.strip().split()
        if len(name_parts) >= 2:
            first_name = " ".join(name_parts[:-1])
            last_name = name_parts[-1]
        else:
            first_name = name_parts[0] if name_parts else "Unknown"
            last_name = "Author"

        existing_authors = await self.author_repo.search(author_name)
        if existing_authors:
            return existing_authors[0]["id"]

        author_create = AuthorCreate(first_name=first_name, last_name=last_name)
        author = await self.author_repo.create(author_create)
        return author["id"]
