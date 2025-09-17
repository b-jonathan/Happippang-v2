import os
from functools import lru_cache
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as SyncEngine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


Base = declarative_base()


@lru_cache
def get_async_engine() -> AsyncEngine:
    url = os.getenv("DATABASE_URL")
    return create_async_engine(url, pool_pre_ping=True, future=True)


@lru_cache
def get_sync_engine() -> SyncEngine:
    engine = get_async_engine()
    sync_url = engine.url.render_as_string(hide_password=False).replace(
        "+asyncpg", "+psycopg2"
    )
    return create_engine(sync_url, future=True)


async_engine = get_async_engine()
sync_engine = get_sync_engine()

# --------------------------------------------------------------------
# 2)  Session factory
# --------------------------------------------------------------------
async_session_maker = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# --------------------------------------------------------------------
# 3)  FastAPI dependency
# --------------------------------------------------------------------
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a fresh AsyncSession and guarantees close/rollback/commit
    exactly once per request.  Import this in your routers like:

        from backend.apputils.db import get_session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
