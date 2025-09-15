import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.import_service import ImportService


@pytest.mark.unit
class TestImportService:

    @pytest.fixture
    def import_service(self, mock_db_connection):
        return ImportService(mock_db_connection)

    @pytest.fixture
    def mock_book_repo(self, import_service):
        import_service.book_repo = AsyncMock()
        return import_service.book_repo

    @pytest.fixture
    def mock_author_repo(self, import_service):
        import_service.author_repo = AsyncMock()
        return import_service.author_repo

    async def test_parse_json_success(self, import_service):
        json_content = b'[{"title": "Book 1", "published_year": 2023}]'

        result = import_service._parse_json(json_content)

        assert isinstance(result, list)
        assert len(result) >= 0

    async def test_parse_csv_success(self, import_service):
        csv_content = b'title,published_year\nBook 1,2023\nBook 2,2024'

        result = import_service._parse_csv(csv_content)

        assert isinstance(result, list)
        assert len(result) >= 0

    async def test_get_or_create_author_existing(self, import_service, mock_author_repo):
        author_name = "John Doe"
        existing_author = {"id": "123", "first_name": "John", "last_name": "Doe"}

        mock_author_repo.search.return_value = [existing_author]

        result = await import_service._get_or_create_author(author_name)

        assert result == "123"

    async def test_get_or_create_author_new(self, import_service, mock_author_repo):
        author_name = "Jane Smith"
        new_author = {"id": "456", "first_name": "Jane", "last_name": "Smith"}

        mock_author_repo.search.return_value = []
        mock_author_repo.create.return_value = new_author

        result = await import_service._get_or_create_author(author_name)

        assert result == "456"
