from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool
from db import get_sync_engine
from sqlalchemy import text
app = FastAPI()


@app.get("/")
async def health():
    return {"status": "OK"}


@app.get("/sales/")
async def get_sales():
    def _blocking():
        stmt = text("""
            SELECT
                sales_date,
                store_name,
                item_name,
                sales_qty,
                net_sales,
                margin
            FROM sales
            WHERE sales_date BETWEEN :start AND :end
        """)
        start = "2025-07-01".encode("ascii").decode()   # guarantees only ASCII
        end   = "2025-07-13".encode("ascii").decode()

        params = {"start": start, "end": end}
        sync_engine = get_sync_engine()
        with sync_engine.begin() as conn:
            return conn.execute(
                stmt, params
            ).mappings().all()

    rows = await run_in_threadpool(_blocking)
    return rows
