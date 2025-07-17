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

# ---------- blocking helpers ---------------------------------------- #

def _fetch_sales(start: date, end: date) -> pd.DataFrame:
    stmt = text("""
        SELECT
            sales_date,
            store_name,
            item_name,
            sales_qty
        FROM sales
        WHERE sales_date BETWEEN :start AND :end
    """)
    with get_sync_engine().begin() as conn:
        rows = conn.execute(stmt, {"start": start, "end": end}).mappings().all()

    if not rows:
        raise HTTPException(404, "no rows in that date window")

    df = pd.DataFrame(rows)
    df.rename(columns={"sales_date": "ds", "sales_qty": "y"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"])        # Prophet‑friendly dtype
    return df


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


# ---------- routes --------------------------------------------------- #

@app.get("/forecast/", tags=["forecast"])
async def forecast(
    start: date = Query(date(2025, 7, 1)),
    end:   date = Query(date(2025, 7, 13)),
    horizon: int = Query(30, ge=1, le=90),
):
    """Return Prophet forecasts for every store‑item pair in the window."""
    def _blocking():
        df = _fetch_sales(start, end)
        return _build_forecasts(df, horizon)

    return await run_in_threadpool(_blocking)