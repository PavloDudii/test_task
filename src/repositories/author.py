from typing import List, Optional, Dict, Any
from uuid import UUID
from .base import BaseRepository
from ..schemas.author import AuthorCreate, AuthorUpdate


class AuthorRepository(BaseRepository):

    async def create(self, author_data: AuthorCreate) -> Dict[str, Any]:
        query = """
            INSERT INTO authors (first_name, last_name, biography)
            VALUES ($1, $2, $3)
            RETURNING *
        """
        return await self.fetch_one(
            query, author_data.first_name, author_data.last_name, author_data.biography
        )

    async def get_by_id(self, author_id: UUID) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM authors WHERE id = $1"
        return await self.fetch_one(query, author_id)

    async def get_all(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM authors 
            ORDER BY last_name, first_name 
            LIMIT $1 OFFSET $2
        """
        return await self.fetch_all(query, limit, offset)

    async def get_total_count(self) -> int:
        query = "SELECT COUNT(*) FROM authors"
        return await self.connection.fetchval(query)

    async def update(
        self, author_id: UUID, author_data: AuthorUpdate
    ) -> Optional[Dict[str, Any]]:
        update_fields = []
        values = []
        param_count = 0

        for field, value in author_data.dict(exclude_unset=True).items():
            param_count += 1
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)

        if not update_fields:
            return await self.get_by_id(author_id)

        param_count += 1
        values.append(author_id)

        query = f"""
            UPDATE authors 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """
        return await self.fetch_one(query, *values)

    async def delete(self, author_id: UUID) -> bool:
        query = "DELETE FROM authors WHERE id = $1"
        result = await self.execute(query, author_id)
        return "DELETE 1" in result

    async def search(
        self, search_term: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM authors 
            WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER($1)
            ORDER BY last_name, first_name
            LIMIT $2 OFFSET $3
        """
        return await self.fetch_all(query, f"%{search_term}%", limit, offset)
