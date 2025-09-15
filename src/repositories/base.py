from typing import Any, Dict, List, Optional
import asyncpg
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        rows = await self.connection.fetch(query, *args)
        return [dict(row) for row in rows]

    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        row = await self.connection.fetchrow(query, *args)
        return dict(row) if row else None

    async def execute(self, query: str, *args) -> str:
        """Execute command and return status"""
        return await self.connection.execute(query, *args)
