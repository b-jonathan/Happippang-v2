# save_to_postgres.py
"""
Load sales data from the Excel workbook shipped by the stores,
normalise/clean it the same way our Prophet pipeline expects,
and append it to a PostgreSQL fact table.

Usage (POSIX / PowerShell)
-------------------------
$ python save_to_postgres.py --xlsx ../../data/hero.xlsx --start 2025-07-01 --end 2025-07-13

Environment variables expected
------------------------------
PGUSER, PGPASSWORD, PGHOST, PGDATABASE, PGPORT  (defaults: reader/secret/localhost/sales/5432)

Notes
-----
• Will create table *fact_daily_sales* with reasonable dtypes if it does not exist.
• Uses pandas.to_sql with *method="multi"* for batched INSERTs.
• Duplicate prevention is left to the SQL layer (unique constraint on (sales_date, store_name, item_name)).
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import (BIGINT, DATE, FLOAT, NUMERIC, TEXT, VARCHAR, Column, Engine,
                        MetaData, Table, UniqueConstraint, inspect, MetaData, select, create_engine as create_sync_engine )
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncio

from db import get_sync_engine, get_async_engine

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def clean_dataframe(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # Drop unused columns
    df.drop(
        columns=[
            "STORE_CODE",
            "SUBFAMILY_CODE",
            "SUBFAMILY_NAME",
            "ITEM_CODE",
            "VENDOR_CODE",
            "VENDOR_NAME",
            "CONSIGNMENT_FLAG",
        ],
        inplace=True,
        errors="ignore",
    )

    # Normalise data types and contents
    df["SALES_DATE"] = pd.to_datetime(df["SALES_DATE"], errors="coerce").dt.date
    df["ITEM_NAME"] = df["ITEM_NAME"].str.removeprefix("'HAPPIPPANG").str.strip()
    df["STORE_NAME"] = df["STORE_NAME"].str.removeprefix("'").str.strip()

    # Standard column order / names for DB
    df.rename(
        columns={
            "SALES_DATE": "sales_date",
            "STORE_NAME": "store_name",
            "ITEM_NAME": "item_name",
            "SALES_QTY": "sales_qty",
            "SALES_AMOUNT_INC_VAT": "sales_amount_inc_vat",
            "VAT_AMOUNT": "vat_amount",
            "NET_SALES": "net_sales",
            "TOTAL_COST": "total_cost",
            "MARGIN": "margin",
            "MARGIN_PERCENT": "margin_percent",
        },
        inplace=True,
    )

    return df

meta = MetaData()

sales_table = Table(
    "sales",
    meta,
    Column("sales_date", DATE, nullable=False),
    Column("store_name", VARCHAR(120), nullable=False),
    Column("item_name", VARCHAR(120), nullable=False),
    Column("sales_qty", BIGINT, nullable=False),
    Column("sales_amount_inc_vat", NUMERIC(14, 2), nullable=False),
    Column("vat_amount", NUMERIC(14, 2), nullable=False),
    Column("net_sales", NUMERIC(14, 2), nullable=False),
    Column("total_cost", NUMERIC(14, 2), nullable=False),
    Column("margin", NUMERIC(14, 2), nullable=False),
    Column("margin_percent", NUMERIC(14, 2), nullable=False),
    # UniqueConstraint("sales_date", "store_name", "item_name", name="uix_sales"),
)

###############################################################################
# Core I/O functions
###############################################################################

async def ensure_table(engine: AsyncEngine) -> None:
    """Create fact_daily_sales if it doesn't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)


async def bulk_upsert(df: pd.DataFrame, engine: AsyncEngine, truncate: bool) -> None:

    # swap +asyncpg → +psycopg2 for a blocking engine
    sync_engine = get_sync_engine()

    def _upload() -> None:
        with sync_engine.begin() as conn:
            if truncate:
                conn.execute(sales_table.delete())
            df.to_sql(
                name=sales_table.name,
                con=conn,
                index=False,
                if_exists="append",
                method="multi",
                chunksize=1000,
            )

    # run the blocking upload in a worker thread
    await asyncio.to_thread(_upload)
    await asyncio.to_thread(sync_engine.dispose)
    

async def reflect_and_query():
     async with engine.begin() as conn:          # conn is AsyncConnection
        # 1) discover table names
        table_names = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        print("tables:", table_names)
        

       
# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------



if __name__ == "__main__":
    engine = get_async_engine()
    async def main():
        try:
        # 1. Ensure table exists
            await reflect_and_query()
            await ensure_table(engine)

        # 2. Read & clean workbook
            raw = pd.read_excel("../../data/hero.xlsx")
            df = clean_dataframe(raw)

        # # 3. Upsert / append
            await bulk_upsert(df, engine, truncate=True)

            print(f"Loaded {len(df):,} rows into sales")
        finally:
            await engine.dispose()
    asyncio.run(main())