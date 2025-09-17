# backend/alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import url as sa_url

# Make the repo root importable so "import backend..." always works
# env.py lives in backend/alembic, so go two levels up
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import backend.app.models as app  # ensure models are imported
from alembic import context
from backend.app.utils.db import Base  # your declarative Base

_ = app  # silence linter

# Alembic Config
config = context.config

# Read and normalize the URL for sync migrations
raw = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")
if not raw:
    raise RuntimeError("DATABASE_URL env var not set")

u = sa_url.make_url(raw)

# Force a sync driver for Alembic runs
if u.drivername in (
    "postgres",
    "postgresql",
    "postgresql+asyncpg",
    "postgresql+psycopg2",
):
    u = u.set(drivername="postgresql+psycopg")

# Translate async style ssl flags to libpq style
q = dict(u.query)
if "ssl" in q:
    ssl_val = str(q.pop("ssl")).lower()
    if ssl_val in ("1", "true", "yes", "require"):
        q["sslmode"] = "require"
# channel_binding is not used for migrations
q.pop("channel_binding", None)
u = u.set(query=q)

config.set_main_option("sqlalchemy.url", str(u))

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
