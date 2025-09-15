import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from src.api.v1.book import router as books_router
from src.core.database import get_db
from src.api.v1.auth import get_current_user
from src.schemas.book import Book, BookCreate, BookUpdate, BulkImportResponse
from src.schemas.pagination import PaginatedResponse

@pytest.mark.asyncio
async def test_create_book_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)

    async def fake_get_db():
        return mock_db_connection

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    book_data = {
        "title": "Test Book",
        "content": "Test Content",
        "description": "Test Description",
        "published_year": 2023,
        "genre": "Fiction",
        "author_id": str(uuid4())
    }

    with patch("src.api.v1.book.BookService.create_book", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Book(
            id=uuid4(),
            **book_data,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/books/", json=book_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_books_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_db] = lambda: mock_db_connection

    sample_book = {
        "id": str(uuid4()),
        "title": "Test Book",
        "content": "Content Content",
        "description": "Desc",
        "published_year": 2023,
        "genre": "Fiction",
        "author_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with patch("src.api.v1.book.BookService.get_books", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = PaginatedResponse(
            items=[Book(**sample_book)],
            total=1,
            page=1,
            size=20
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/books/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Book"
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_book_by_id_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_db] = lambda: mock_db_connection

    book_id = uuid4()
    sample_book = {
        "id": str(book_id),
        "title": "Test Book",
        "content": "Content Content",
        "description": "Desc",
        "published_year": 2023,
        "genre": "Fiction",
        "author_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with patch("src.api.v1.book.BookService.get_book_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Book(**sample_book)

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/books/{book_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(book_id)
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_book_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_db] = lambda: mock_db_connection
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    book_id = uuid4()
    update_data = {"title": "Updated Title"}

    with patch("src.api.v1.book.BookService.update_book", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = Book(
            id=book_id,
            title="Updated Title",
            content="Content Content",
            description="Desc",
            published_year=2023,
            genre="Fiction",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(f"/books/{book_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    mock_update.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_book_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_db] = lambda: mock_db_connection
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    book_id = uuid4()

    with patch("src.api.v1.book.BookService.delete_book", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(f"/books/{book_id}")

    assert response.status_code == 204
    mock_delete.assert_awaited_once()

@pytest.mark.asyncio
async def test_import_books_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(books_router)
    app.dependency_overrides[get_db] = lambda: mock_db_connection
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    file_content = b'[]'

    with patch("src.api.v1.book.ImportService.import_from_file", new_callable=AsyncMock) as mock_import:
        mock_import.return_value = BulkImportResponse(
            success_count=2,
            error_count=0,
            errors=[]
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/books/import",
                files={"file": ("books.json", file_content, "application/json")}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["success_count"] == 2
    assert data["error_count"] == 0
    assert data["errors"] == []
    mock_import.assert_awaited_once()
