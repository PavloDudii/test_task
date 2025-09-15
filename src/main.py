import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from src.core.database import database
from src.core.rate_limit import RateLimiterMiddleware
from src.api.v1.author import router as author_router
from src.api.v1.book import router as book_router
from src.api.v1.auth import router as auth_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            await database.connect()
            logger.info("Database connected successfully")
            break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_interval)
            else:
                logger.error("Max database connection retries reached")
                raise

    yield

    await database.disconnect()
    logger.info("Application shutdown complete")


app = FastAPI(prefix="/api/v1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests=10,
    window=60,
)

app.include_router(book_router)
app.include_router(author_router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    try:
        async with database.get_connection() as connection:
            await connection.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/")
async def root():
    return {
        "message": "Book Management System",
        "docs": "/api/v1/docs",
        "health": "/health",
    }
