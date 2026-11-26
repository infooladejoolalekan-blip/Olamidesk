"""
database.py
Async SQLAlchemy engine and session management for PostgreSQL.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings
from models import Base

logger = logging.getLogger(__name__)


def _normalize_db_url(url: str) -> str:
    """
    Railway provides DATABASE_URL as postgresql://... 
    SQLAlchemy's async engine needs postgresql+asyncpg://...
    Also handle older postgres:// prefix.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


_db_url = _normalize_db_url(settings.database_url)

# pool_pre_ping checks connection health before use; recycle prevents stale connections.
engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Async context manager yielding a database session. Auto-commits on success."""
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Create all tables if they do not exist. Called once on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized — all tables are ready.")


async def close_db() -> None:
    """Dispose the engine cleanly on shutdown."""
    await engine.dispose()
    logger.info("Database connection closed.")