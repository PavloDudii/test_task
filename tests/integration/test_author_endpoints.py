import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from src.api.v1.author import router as authors_router
from src.core.database import get_db
from src.schemas.author import Author, AuthorCreate, AuthorUpdate
from src.schemas.pagination import PaginatedResponse

@pytest.mark.asyncio
async def test_create_author_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(authors_router)

    # Мок current_user
    from src.api.v1.auth import get_current_user
    async def fake_get_db():
        return mock_db_connection
    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    author_data = {"first_name": "John", "last_name": "Doe"}

    with patch("src.api.v1.author.AuthorService.create_author", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Author(
            id=uuid4(),
            first_name=author_data["first_name"],
            last_name=author_data["last_name"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/authors/", json=author_data)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_authors_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(authors_router)
    async def fake_get_db():
        return mock_db_connection
    app.dependency_overrides[get_db] = fake_get_db

    sample_author = {
        "id": str(uuid4()),
        "first_name": "John",
        "last_name": "Doe",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with patch("src.api.v1.author.AuthorService.get_authors", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = PaginatedResponse(
            items=[Author(**sample_author)],
            total=1,
            page=1,
            size=20
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/authors/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["first_name"] == "John"
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_author_by_id_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(authors_router)
    async def fake_get_db():
        return mock_db_connection
    app.dependency_overrides[get_db] = fake_get_db

    author_id = uuid4()
    sample_author = {
        "id": str(author_id),
        "first_name": "John",
        "last_name": "Doe",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with patch("src.api.v1.author.AuthorService.get_author_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Author(**sample_author)


        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/authors/{author_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(author_id)
    mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_author_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(authors_router)
    async def fake_get_db():
        return mock_db_connection
    app.dependency_overrides[get_db] = fake_get_db

    from src.api.v1.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    author_id = uuid4()
    update_data = {"first_name": "Jane", "last_name": "Smith"}

    with patch("src.api.v1.author.AuthorService.update_author", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = Author(
            id=author_id,
            first_name=update_data["first_name"],
            last_name=update_data["last_name"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(f"/authors/{author_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    mock_update.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_author_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(authors_router)
    async def fake_get_db():
        return mock_db_connection
    app.dependency_overrides[get_db] = fake_get_db

    from src.api.v1.auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: {"id": uuid4()}

    author_id = uuid4()

    with patch("src.api.v1.author.AuthorService.delete_author", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(f"/authors/{author_id}")

    assert response.status_code == 204
    mock_delete.assert_awaited_once()
