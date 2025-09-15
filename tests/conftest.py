import pytest
import asyncio
import inspect
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def pytest_collection_modifyitems(items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture
async def mock_db_connection():
    """Mock database connection"""
    connection = AsyncMock()
    connection.transaction = AsyncMock()
    connection.transaction.return_value.__aenter__ = AsyncMock()
    connection.transaction.return_value.__aexit__ = AsyncMock()
    return connection


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "id": uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed_password_123",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_author_data():
    """Sample author data for tests"""
    return {
        "id": uuid4(),
        "first_name": "John",
        "last_name": "Doe",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_book_data():
    """Sample book data for tests"""
    author_id = uuid4()
    return {
        "id": uuid4(),
        "title": "Test Book",
        "content": "Test content",
        "description": "Test description",
        "published_year": 2023,
        "genre": "Fiction",
        "author_id": author_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
