from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from src.services.book_service import BookService
from src.schemas.book import BookCreate, BookUpdate, BookFilters, Genre


@pytest.mark.unit
class TestBookService:

    @pytest.fixture
    def book_service(self, mock_db_connection):
        return BookService(mock_db_connection)

    @pytest.fixture
    def mock_book_repo(self, book_service):
        book_service.book_repo = AsyncMock()
        return book_service.book_repo

    @pytest.fixture
    def mock_author_repo(self, book_service):
        book_service.author_repo = AsyncMock()
        return book_service.author_repo

    async def test_create_book_success(self, book_service, mock_book_repo, mock_author_repo, sample_book_data,
                                       sample_author_data):
        book_data = BookCreate(
            title="New Book",
            content="Content Content",
            description="Description",
            published_year=2023,
            genre=Genre.fantasy,
            author_id=sample_author_data["id"],
        )

        mock_author_repo.get_by_id.return_value = sample_author_data
        mock_book_repo.create.return_value = sample_book_data

        result = await book_service.create_book(book_data)

        assert hasattr(result, 'title')
        assert hasattr(result, 'content')
        mock_book_repo.create.assert_called_once_with(book_data)

    async def test_create_book_invalid_author(self, book_service, mock_book_repo, mock_author_repo):
        book_data = BookCreate(
            title="New Book",
            content="Content Content",
            description="Description",
            published_year=2023,
            genre=Genre.fantasy,
            author_id=uuid4()
        )

        mock_author_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await book_service.create_book(book_data)

    async def test_get_book_by_id_success(self, book_service, mock_book_repo, mock_author_repo, sample_book_data,
                                          sample_author_data):
        book_id = sample_book_data["id"]

        mock_book_repo.get_by_id.return_value = sample_book_data
        mock_author_repo.get_by_id.return_value = sample_author_data

        result = await book_service.get_book_by_id(book_id)

        assert result.id == book_id
        assert hasattr(result, 'title')

    async def test_get_book_by_id_not_found(self, book_service, mock_book_repo):
        book_id = uuid4()
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await book_service.get_book_by_id(book_id)

    async def test_get_books_with_filters(self, book_service, mock_book_repo):
        filters = BookFilters(genre=Genre.fiction)

        mock_books = [
            {
                "id": uuid4(),
                "title": "Book 1",
                "content": "Content 1",
                "description": "Desc 1",
                "published_year": 2023,
                "genre": "Fiction",
                "author_id": uuid4(),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": uuid4(),
                "title": "Book 2",
                "content": "Content 2",
                "description": "Desc 2",
                "published_year": 2023,
                "genre": "Fiction",
                "author_id": uuid4(),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]

        mock_book_repo.get_all.return_value = mock_books
        mock_book_repo.get_total_count.return_value = 2

        with patch.object(book_service, "_format_book_response", side_effect=lambda b: b):
            result = await book_service.get_books(filters, page=1, size=10)

        assert result.total == 2
        assert len(result.items) == 2
        for book in result.items:
            assert book["genre"] == "Fiction"

    async def test_update_book_success(self, book_service, mock_book_repo, mock_author_repo, sample_book_data):
        book_id = sample_book_data["id"]
        update_data = BookUpdate(title="Updated Title")

        mock_book_repo.get_by_id.return_value = sample_book_data
        updated_data = {**sample_book_data, "title": "Updated Title"}
        mock_book_repo.update.return_value = updated_data
        mock_author_repo.get_by_id.return_value = None  # No author update

        result = await book_service.update_book(book_id, update_data)

        assert hasattr(result, 'title')
        mock_book_repo.update.assert_called_once()

    async def test_delete_book_success(self, book_service, mock_book_repo, sample_book_data):
        book_id = sample_book_data["id"]

        mock_book_repo.get_by_id.return_value = sample_book_data
        mock_book_repo.delete.return_value = True

        result = await book_service.delete_book(book_id)

        assert result is True
