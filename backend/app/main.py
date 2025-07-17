from datetime import date
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from starlette.concurrency import run_in_threadpool
from prophet import Prophet
from db import get_sync_engine
from sqlalchemy import text
app = FastAPI()


@app.get("/")
async def health():
    return {"status": "OK"}


# ---------- blocking SQL ------------------------------------------------- #

def fetch_sales_rows(start: date, end: date):
    """Pure blocking code — runs on any thread."""
    stmt = text("""
        SELECT sales_date,
               store_name,
               item_name,
               sales_qty,
               net_sales,
               margin
        FROM sales
        WHERE sales_date BETWEEN :start AND :end
    """)
    with get_sync_engine().begin() as conn:
        return conn.execute(stmt, {"start": start, "end": end}).mappings().all()


# ---------- async helper (thread‑pool wrapper) --------------------------- #


async def get_sales_rows(start: date, end: date):
    return await run_in_threadpool(fetch_sales_rows, start, end)


def _build_forecasts(df: pd.DataFrame, horizon: int) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}

    for (store, item), grp in df.groupby(["store_name", "item_name"]):
        ts = (
            grp[["ds", "y"]]
            .groupby("ds", as_index=False).sum()   # one row per day
            .sort_values("ds")
        )

        if len(ts) < 2 or ts["y"].nunique() < 2:
            # skip series Prophet cannot fit
            continue

        m = Prophet().fit(ts)
        future = m.make_future_dataframe(horizon)
        fc = m.predict(future).tail(horizon)[["ds", "yhat", "yhat_lower", "yhat_upper"]]

        key = f"{store}::{item}"
        out[key] = fc.to_dict(orient="records")

    return out
# ---------- FastAPI routes ---------------------------------------------- #

@app.get("/sales/")
async def get_sales(
    start: date = Query(date(2025, 7, 1)),
    end:   date = Query(date(2025, 7, 13)),
):
    # just call the async wrapper
    return await get_sales_rows(start, end)


@app.get("/forecast/")
async def get_forecast(
    start: date = Query(date(2025, 7, 1)),
    end:   date = Query(date(2025, 7, 13)),
    horizon: int = Query(30, ge=1, le=90),
):
    rows = await get_sales_rows(start, end)    # no duplication, no coroutine mishaps

    # build DataFrame once
    df = (
        pd.DataFrame([dict(r) for r in rows])
        .rename(columns={"sales_date": "ds", "sales_qty": "y"})
    )
    df["ds"] = pd.to_datetime(df["ds"])

    forecasts = _build_forecasts(df, horizon)
    return forecasts
