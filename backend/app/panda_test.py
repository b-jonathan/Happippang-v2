import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from pathlib import Path

from sqlalchemy import text

from utils.util import slugify
from db import get_sync_engine

# create a new column with safe names


sync_engine = get_sync_engine()

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


with sync_engine.begin() as conn:
    df = pd.read_sql(stmt, conn, params=params)
    
print(df)

models = {}
forecasts = {}

out_dir = Path("./forecasts")
out_dir.mkdir(exist_ok=True)

for (store, item), grp in df.groupby(["store_name", "item_name"]):
    if len(grp) < 2:                 # skip thin series
        continue

    ts = grp[["ds", "y"]].copy()

    m = Prophet().fit(ts)
    future = m.make_future_dataframe(30)
    fc = m.predict(future)

    key = (store, item)
    models[key] = m
    forecasts[key] = fc

    # create nested folder per store once
    store_dir = out_dir / store
    store_dir.mkdir(exist_ok=True)

    safe_file = f"{slugify(item)}.png"
    fig = m.plot(fc, xlabel="Date", ylabel="Sales Qty")
    fig.suptitle(f"{item} – {store}", fontsize=12)
    fig.savefig(store_dir / safe_file)
    plt.close(fig)

print(f"Built {len(models)} item-level forecasts.  Plots saved to {out_dir.resolve()}")

# summary = (
#     df.groupby("ITEM_NAME", as_index=False)
#       .agg(
#           total_qty            = ("SALES_QTY",            "sum"),
#           gross_sales_vat_inc  = ("SALES_AMOUNT_INC_VAT", "sum"),
#           vat_paid             = ("VAT_AMOUNT",           "sum"),
#           net_sales            = ("NET_SALES",            "sum"),
#           total_cost           = ("TOTAL_COST",           "sum"),
#           margin               = ("MARGIN",               "sum"),
#       )
# )

# # weighted margin %
# summary["margin_percent"] = (summary["margin"] / summary["net_sales"] * 100).round(2)

# # sort if you want the best‑selling items first
# summary = summary.sort_values("gross_sales_vat_inc", ascending=False)

