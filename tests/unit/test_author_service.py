from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.author_service import AuthorService
from src.schemas.author import AuthorCreate, AuthorUpdate


@pytest.mark.unit
class TestAuthorService:

    @pytest.fixture
    def author_service(self, mock_db_connection):
        return AuthorService(mock_db_connection)

    @pytest.fixture
    def mock_author_repo(self, author_service):
        author_service.author_repo = AsyncMock()
        return author_service.author_repo

    async def test_create_author_success(self, author_service, mock_author_repo):
        author_data = AuthorCreate(first_name="John", last_name="Doe")
        expected_result = {
            "id": uuid4(),
            "first_name": "John",
            "last_name": "Doe",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        mock_author_repo.create.return_value = expected_result

        result = await author_service.create_author(author_data)

        assert result.first_name == "John"
        assert result.last_name == "Doe"
        mock_author_repo.create.assert_called_once_with(author_data)

    async def test_get_author_by_id_success(self, author_service, mock_author_repo, sample_author_data):
        author_id = sample_author_data["id"]
        mock_author_repo.get_by_id.return_value = sample_author_data

        result = await author_service.get_author_by_id(author_id)

        assert result.id == author_id
        assert result.first_name == sample_author_data["first_name"]

    async def test_get_author_by_id_not_found(self, author_service, mock_author_repo):
        author_id = uuid4()
        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await author_service.get_author_by_id(author_id)

    async def test_get_authors_with_pagination(self, author_service, mock_author_repo):
        mock_authors = [
            {"id": uuid4(), "first_name": "John", "last_name": "Doe", "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": uuid4(), "first_name": "Jane", "last_name": "Smith", "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
        ]

        mock_author_repo.get_all.return_value = mock_authors
        mock_author_repo.get_total_count.return_value = 2

        result = await author_service.get_authors(page=1, size=10)

        assert len(result.items) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.size == 10

    async def test_update_author_success(self, author_service, mock_author_repo, sample_author_data):
        author_id = sample_author_data["id"]
        update_data = AuthorUpdate(first_name="Updated John")

        mock_author_repo.get_by_id.return_value = sample_author_data
        updated_data = {**sample_author_data, "first_name": "Updated John"}
        mock_author_repo.update.return_value = updated_data

        result = await author_service.update_author(author_id, update_data)

        assert result.first_name == "Updated John"
        mock_author_repo.update.assert_called_once_with(author_id, update_data)

    async def test_update_author_not_found(self, author_service, mock_author_repo):
        author_id = uuid4()
        update_data = AuthorUpdate(first_name="Updated")

        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await author_service.update_author(author_id, update_data)

    async def test_delete_author_success(self, author_service, mock_author_repo, sample_author_data):
        author_id = sample_author_data["id"]

        mock_author_repo.get_by_id.return_value = sample_author_data
        mock_author_repo.delete.return_value = True

        result = await author_service.delete_author(author_id)

        assert result is True
        mock_author_repo.delete.assert_called_once_with(author_id)

    async def test_delete_author_not_found(self, author_service, mock_author_repo):
        author_id = uuid4()
        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await author_service.delete_author(author_id)
