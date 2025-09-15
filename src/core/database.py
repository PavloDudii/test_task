import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from src.core.settings import settings
import logging


logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )
            logger.info("Connected to database")
            return self.pool

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            logger.info(f"Disconnected from database")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self.pool:
            raise RuntimeError("Database pool is not initialized.")

        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database connection error: {e}")
                raise


database = Database()


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    async with database.get_connection() as connection:
        yield connection
