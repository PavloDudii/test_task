from uuid import UUID
import asyncpg
from fastapi import HTTPException, status
from src.repositories.author import AuthorRepository
from src.schemas.author import AuthorCreate, AuthorUpdate, Author
from src.schemas.pagination import PaginatedResponse


class AuthorService:
    def __init__(self, connection: asyncpg.Connection):
        self.author_repo = AuthorRepository(connection)

    async def create_author(self, author_data: AuthorCreate) -> Author:
        author = await self.author_repo.create(author_data)
        return Author(**author)

    async def get_author_by_id(self, author_id: UUID) -> Author:
        author = await self.author_repo.get_by_id(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with id {author_id} not found",
            )
        return Author(**author)

    async def get_authors(
        self, page: int = 1, size: int = 20
    ) -> PaginatedResponse[Author]:
        offset = (page - 1) * size
        authors = await self.author_repo.get_all(size, offset)
        total = await self.author_repo.get_total_count()

        return PaginatedResponse(
            items=[Author(**author) for author in authors],
            total=total,
            page=page,
            size=size,
        )

    async def update_author(self, author_id: UUID, author_data: AuthorUpdate) -> Author:
        existing = await self.author_repo.get_by_id(author_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with id {author_id} not found",
            )

        updated_author = await self.author_repo.update(author_id, author_data)
        return Author(**updated_author)

    async def delete_author(self, author_id: UUID) -> bool:
        existing = await self.author_repo.get_by_id(author_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with id {author_id} not found",
            )

        return await self.author_repo.delete(author_id)
