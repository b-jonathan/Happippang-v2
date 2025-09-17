import os
from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.engine import url as sa_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


def _resolve_url_and_connect_args() -> tuple[str, dict]:
    raw = (
        (os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL") or "")
        .strip()
        .strip("'")
        .strip('"')
    )
    if not raw:
        raise RuntimeError("Missing ASYNC_DATABASE_URL or DATABASE_URL")

    u = sa_url.make_url(raw)

    # Force async driver
    if u.drivername in ("postgres", "postgresql", "postgresql+psycopg2"):
        u = u.set(drivername="postgresql+asyncpg")

    q = dict(u.query)
    connect_args: dict = {}

    # Translate sslmode → ssl for asyncpg and clean URL
    sslmode = q.pop("sslmode", None)
    if sslmode and str(sslmode).lower() in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True

    # Support ?ssl=true too
    ssl_q = q.pop("ssl", None)
    if ssl_q and str(ssl_q).lower() in ("1", "true", "yes", "require"):
        connect_args["ssl"] = True

    # Remove params asyncpg does not know
    q.pop("channel_binding", None)

    u = u.set(query=q)

    # Tiny startup log to prove what driver and ssl we use
    try:
        print(f"[DB] driver={u.drivername} ssl={'ssl' in connect_args}")
    except Exception:
        pass

    return str(u), connect_args


@lru_cache
def get_async_engine() -> AsyncEngine:
    url, connect_args = _resolve_url_and_connect_args()
    return create_async_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        poolclass=NullPool,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_async_engine(), expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = get_sessionmaker()
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
