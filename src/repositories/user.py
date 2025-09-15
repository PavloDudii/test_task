from typing import List, Optional, Dict, Any
from uuid import UUID
from src.repositories.base import BaseRepository
from src.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository):

    async def create(
        self, user_data: UserCreate, hashed_password: str
    ) -> Dict[str, Any]:
        """Create a new user with hashed password"""
        query = """
            INSERT INTO users (username, email, full_name, hashed_password, is_active)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, username, email, full_name, is_active, created_at, updated_at
        """
        return await self.fetch_one(
            query,
            user_data.username.lower(),
            user_data.email.lower(),
            user_data.full_name,
            hashed_password,
            user_data.is_active,
        )

    async def get_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
            SELECT id, username, email, full_name, is_active, created_at, updated_at
            FROM users WHERE id = $1
        """
        return await self.fetch_one(query, user_id)

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username including password hash for authentication"""
        query = """
            SELECT id, username, email, full_name, hashed_password, is_active, created_at, updated_at
            FROM users WHERE username = $1
        """
        return await self.fetch_one(query, username.lower())

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = """
            SELECT id, username, email, full_name, is_active, created_at, updated_at
            FROM users WHERE email = $1
        """
        return await self.fetch_one(query, email.lower())

    async def update(
        self, user_id: UUID, user_data: UserUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update user"""
        update_fields = []
        values = []
        param_count = 0

        for field, value in user_data.dict(exclude_unset=True).items():
            if field == "email" and value:
                value = value.lower()

            param_count += 1
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)

        if not update_fields:
            return await self.get_by_id(user_id)

        param_count += 1
        values.append(user_id)

        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING id, username, email, full_name, is_active, created_at, updated_at
        """
        return await self.fetch_one(query, *values)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user (soft delete by setting is_active = false)"""
        query = "UPDATE users SET is_active = false WHERE id = $1"
        result = await self.execute(query, user_id)
        return "UPDATE 1" in result
