from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from fastapi import FastAPI
from src.api.v1.auth import router as auth_router
from src.schemas.user import User

@pytest.mark.asyncio
async def test_register_user_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(auth_router)

    async def fake_get_db():
        return mock_db_connection
    from src.api.v1.auth import get_db
    app.dependency_overrides[get_db] = fake_get_db

    user_data = {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "Password123"
    }

    with patch("src.api.v1.auth.AuthService.register_user", new_callable=AsyncMock) as mock_register:
        mock_register.return_value = User(
            id=uuid4(),
            username=user_data["username"],
            full_name=user_data["full_name"],
            email=user_data["email"],
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    mock_register.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_user_endpoint(mock_db_connection):
    app = FastAPI()
    app.include_router(auth_router)

    async def fake_get_db():
        return mock_db_connection
    from src.api.v1.auth import get_db
    app.dependency_overrides[get_db] = fake_get_db

    login_data = {
        "username": "testuser",
        "password": "Password123"
    }

    with patch("src.api.v1.auth.AuthService.authenticate_user", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"access_token": "jwt_token", "token_type": "bearer", "expires_in":"1800"}

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "jwt_token"
    assert data["token_type"] == "bearer"
    mock_auth.assert_awaited_once()
