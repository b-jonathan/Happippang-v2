import os
from functools import lru_cache
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.engine import url as sa_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

Base = declarative_base()


@lru_cache
def get_async_engine() -> AsyncEngine:
    # Prefer ASYNC_DATABASE_URL, fall back to DATABASE_URL for compatibility
    raw = (
        (os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL") or "")
        .strip()
        .strip("'")
        .strip('"')
    )
    if not raw:
        raise RuntimeError("Missing ASYNC_DATABASE_URL or DATABASE_URL")

    u = sa_url.make_url(raw)

    # Force async driver if a sync one was provided
    if u.drivername in ("postgres", "postgresql", "postgresql+psycopg2"):
        u = u.set(drivername="postgresql+asyncpg")

    # Translate SSL flags for asyncpg and clean unsupported params
    q = dict(u.query)
    connect_args: dict = {}

    sslmode = q.pop("sslmode", None)
    if sslmode and str(sslmode).lower() in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True

    ssl_flag = q.pop("ssl", None)
    if ssl_flag and str(ssl_flag).lower() in ("1", "true", "yes", "require"):
        connect_args["ssl"] = True

    # Remove params asyncpg does not understand
    q.pop("channel_binding", None)

    u = u.set(query=q)

    return create_async_engine(
        str(u),
        connect_args=connect_args,
        pool_pre_ping=True,
        poolclass=NullPool,  # serverless-friendly
        future=True,
    )


async_engine = get_async_engine()

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

        from backend.app.utils.db import get_session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
