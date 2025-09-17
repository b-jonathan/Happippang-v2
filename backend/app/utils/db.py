import logging
import os
from functools import lru_cache
from typing import Any, AsyncGenerator, Dict

from dotenv import load_dotenv
from sqlalchemy.engine import url as sa_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

# ---------------------- Logging ----------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("db")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)
# ----------------------------------------------------

Base = declarative_base()


@lru_cache
def get_async_engine() -> AsyncEngine:
    # Source env remains DATABASE_URL to avoid changing behavior
    src = "DATABASE_URL"
    raw = (os.getenv(src) or "").strip().strip("'").strip('"')
    if not raw:
        logger.error("missing DATABASE_URL")
        raise RuntimeError("Missing or DATABASE_URL")

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

    # One-time cold-start banner to Vercel logs
    banner = (
        f"async engine configured src={src} driver={u.drivername} "
        f"user={u.username} host={u.host} db={u.database} "
        f"ssl={bool(connect_args.get('ssl'))} pool=NullPool"
    )
    logger.info(banner)
    print(f"[DB] {banner}")  # always shows in Function Logs

    return create_async_engine(
        str(u),
        connect_args=connect_args,
        pool_pre_ping=True,
        poolclass=NullPool,  # serverless-friendly
        future=True,
    )


async_engine = get_async_engine()


def engine_public_info() -> Dict[str, Any]:
    """
    Safe snapshot of current engine URL pieces for debug endpoints.
    No secrets are returned.
    """
    u = async_engine.url
    return {
        "driver": u.drivername,
        "user": u.username,
        "host": u.host,
        "database": u.database,
        "query": dict(u.query),
    }


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
    logger.debug("session open")
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("session commit")
        except Exception:
            logger.exception("session rollback due to error")
            await session.rollback()
            raise
        finally:
            logger.debug("session closed")
