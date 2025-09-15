from uuid import UUID
import asyncpg
from datetime import timedelta
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserLogin, User, Token
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.core.exceptions import (
    AuthenticationError,
    DuplicateError,
    NotFoundError,
    http_401_unauthorized,
    http_409_conflict,
)


class AuthService:
    def __init__(self, connection: asyncpg.Connection):
        self.user_repo = UserRepository(connection)

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise http_409_conflict(f"Username '{user_data.username}' already exists")

        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise http_409_conflict(f"Email '{user_data.email}' already exists")

        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repo.create(user_data, hashed_password)

        return User(**user)

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        """Authenticate user and return JWT token"""
        user = await self.user_repo.get_by_username(login_data.username)

        if not user or not verify_password(
            login_data.password, user["hashed_password"]
        ):
            raise http_401_unauthorized("Invalid username or password")

        if not user["is_active"]:
            raise http_401_unauthorized("User account is deactivated")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["id"]), "username": user["username"]},
            expires_delta=access_token_expires,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        )

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        return User(**user)
