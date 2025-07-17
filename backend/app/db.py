from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

import os
from dotenv import load_dotenv
from sqlalchemy.engine import Engine as SyncEngine
from sqlalchemy import create_engine

load_dotenv()

def get_async_engine() -> AsyncEngine:

    url = os.getenv("DATABASE_URL")
    return create_async_engine(url, pool_pre_ping=True, future=True)

def get_sync_engine() -> SyncEngine:
    engine = get_async_engine()
    sync_url =  engine.url.render_as_string(hide_password=False).replace("+asyncpg", "+psycopg2")
    return create_engine(sync_url, future=True)

