from typing import List, Optional, Dict, Any
from uuid import UUID
from .base import BaseRepository
from ..schemas.book import BookCreate, BookUpdate, BookFilters


class BookRepository(BaseRepository):

    async def create(self, book_data: BookCreate) -> Dict[str, Any]:
        query = """
            INSERT INTO books (title, content, description, published_year, genre, author_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """
        return await self.fetch_one(
            query,
            book_data.title,
            book_data.content,
            book_data.description,
            book_data.published_year,
            book_data.genre,
            book_data.author_id,
        )

    async def get_by_id(self, book_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
            SELECT b.*, 
                   a.id as author_id, a.first_name, a.last_name, a.biography,
                   a.created_at as author_created_at, a.updated_at as author_updated_at
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            WHERE b.id = $1
            """
        return await self.fetch_one(query, book_id)

    async def get_all(
        self,
        filters: BookFilters,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> List[Dict[str, Any]]:
        where_conditions = ["1=1"]
        params = []
        param_count = 0

        if filters.title:
            param_count += 1
            where_conditions.append(f"b.title ILIKE ${param_count}")
            params.append(f"%{filters.title}%")

        if filters.author:
            param_count += 1
            where_conditions.append(
                f"(a.first_name ILIKE ${param_count} OR a.last_name ILIKE ${param_count})"
            )
            params.append(f"%{filters.author}%")

        if filters.year_from:
            param_count += 1
            where_conditions.append(
                f"EXTRACT(YEAR FROM b.published_year) >= ${param_count}"
            )
            params.append(filters.year_from)

        if filters.year_to:
            param_count += 1
            where_conditions.append(
                f"EXTRACT(YEAR FROM b.published_year) <= ${param_count}"
            )
            params.append(filters.year_to)

        valid_sorts = {
            "title": "b.title",
            "year": "b.published_year",
            "author": "a.last_name",
        }
        sort_column = valid_sorts.get(sort_by, "b.title")
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        param_count += 1
        params.append(limit)
        param_count += 1
        params.append(offset)

        query = f"""
            SELECT b.*, 
                   a.id as author_id, a.first_name, a.last_name, a.biography,
                   a.created_at as author_created_at, a.updated_at as author_updated_at
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            WHERE {' AND '.join(where_conditions)}
            ORDER BY {sort_column} {sort_direction}
            LIMIT ${param_count - 1} OFFSET ${param_count}
        """

        return await self.fetch_all(query, *params)

    async def get_total_count(self, filters: BookFilters) -> int:
        where_conditions = ["1=1"]
        params = []
        param_count = 0

        if filters.title:
            param_count += 1
            where_conditions.append(f"b.title ILIKE ${param_count}")
            params.append(f"%{filters.title}%")

        if filters.author:
            param_count += 1
            where_conditions.append(
                f"(a.first_name ILIKE ${param_count} OR a.last_name ILIKE ${param_count})"
            )
            params.append(f"%{filters.author}%")

        if filters.year_from:
            param_count += 1
            where_conditions.append(
                f"EXTRACT(YEAR FROM b.published_year) >= ${param_count}"
            )
            params.append(filters.year_from)

        if filters.year_to:
            param_count += 1
            where_conditions.append(
                f"EXTRACT(YEAR FROM b.published_year) <= ${param_count}"
            )
            params.append(filters.year_to)

        query = f"""
            SELECT COUNT(*) FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            WHERE {' AND '.join(where_conditions)}
        """

        return await self.connection.fetchval(query, *params)

    async def update(
        self, book_id: UUID, book_data: BookUpdate
    ) -> Optional[Dict[str, Any]]:
        update_fields = []
        values = []
        param_count = 0

        for field, value in book_data.model_dump(exclude_unset=True).items():
            param_count += 1
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)

        if not update_fields:
            return await self.get_by_id(book_id)

        param_count += 1
        values.append(book_id)

        query = f"""
            UPDATE books 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """
        await self.execute(query, *values)
        return await self.get_by_id(book_id)

    async def delete(self, book_id: UUID) -> bool:
        query = "DELETE FROM books WHERE id = $1"
        result = await self.execute(query, book_id)
        return "DELETE 1" in result
