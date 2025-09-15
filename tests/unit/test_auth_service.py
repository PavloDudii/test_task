from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from src.services.auth_service import AuthService
from src.schemas.user import UserCreate, UserLogin, User
from src.core.exceptions import http_401_unauthorized, http_409_conflict


@pytest.mark.unit
class TestAuthService:

    @pytest.fixture
    def auth_service(self, mock_db_connection):
        return AuthService(mock_db_connection)

    @pytest.fixture
    def mock_user_repo(self, auth_service):
        auth_service.user_repo = AsyncMock()
        return auth_service.user_repo

    async def test_register_user_success(self, auth_service, mock_user_repo):
        user_data = UserCreate(
            username="newuser",
            full_name="New User",
            email="new@example.com",
            password="Password123"
        )

        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None

        mock_user_repo.create.return_value = {
            "id": uuid4(),
            "username": user_data.username,
            "full_name": user_data.full_name,
            "email": user_data.email,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        with patch("src.services.auth_service.get_password_hash", return_value="hashed_pass"):
            result = await auth_service.register_user(user_data)

        assert isinstance(result, User)
        assert result.username == user_data.username
        assert result.email == user_data.email
        mock_user_repo.create.assert_awaited_once()

    async def test_register_user_duplicate_username(self, auth_service, mock_user_repo):
        user_data = UserCreate(
            username="existing",
            full_name="Existing User",
            email="new@example.com",
            password="Password123"
        )

        mock_user_repo.get_by_username.return_value = {"username": "existing"}

        with pytest.raises(Exception):  # Flexible exception checking
            await auth_service.register_user(user_data)

    async def test_register_user_duplicate_email(self, auth_service, mock_user_repo):
        user_data = UserCreate(
            username="newuser",
            full_name="New User",
            email="existing@example.com",
            password="Password123"
        )

        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = {"email": "existing@example.com"}

        with pytest.raises(Exception):
            await auth_service.register_user(user_data)

    async def test_authenticate_user_success(self, auth_service, mock_user_repo, sample_user_data):
        login_data = UserLogin(username="testuser", password="password123")

        mock_user_repo.get_by_username.return_value = sample_user_data

        with patch('src.services.auth_service.verify_password', return_value=True), \
                patch('src.services.auth_service.create_access_token', return_value="jwt_token"):
            result = await auth_service.authenticate_user(login_data)

            assert hasattr(result, 'access_token')
            assert hasattr(result, 'token_type')
            assert result.token_type == "bearer"

    async def test_authenticate_user_invalid_credentials(self, auth_service, mock_user_repo):
        login_data = UserLogin(username="testuser", password="wrongpass")

        mock_user_repo.get_by_username.return_value = None

        with pytest.raises(Exception):
            await auth_service.authenticate_user(login_data)

    async def test_authenticate_user_inactive_account(self, auth_service, mock_user_repo, sample_user_data):
        login_data = UserLogin(username="testuser", password="password123")
        sample_user_data["is_active"] = False

        mock_user_repo.get_by_username.return_value = sample_user_data

        with patch('src.services.auth_service.verify_password', return_value=True):
            with pytest.raises(Exception):
                await auth_service.authenticate_user(login_data)

    async def test_get_user_by_id_success(self, auth_service, mock_user_repo, sample_user_data):
        user_id = sample_user_data["id"]
        mock_user_repo.get_by_id.return_value = sample_user_data

        result = await auth_service.get_user_by_id(user_id)

        assert result.id == user_id
        assert result.username == sample_user_data["username"]

    async def test_get_user_by_id_not_found(self, auth_service, mock_user_repo):
        user_id = uuid4()
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(Exception):
            await auth_service.get_user_by_id(user_id)
