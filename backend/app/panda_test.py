import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from pathlib import Path
import re


def slugify(text: str) -> str:
    """Return a filename‑safe version of any string."""
    text = re.sub(r'[\\/:"*?<>|]+', "_", text)   # replace path separators and illegal chars
    text = re.sub(r"\s+", "_", text.strip())     # collapse whitespace
    return text

# create a new column with safe names


df = pd.read_excel("../../data/hero.xlsx")
df.drop(columns=["STORE_CODE","SUBFAMILY_CODE","SUBFAMILY_NAME","ITEM_CODE","VENDOR_CODE","VENDOR_NAME","CONSIGNMENT_FLAG"], inplace=True)
df["SALES_DATE"] = pd.to_datetime(df["SALES_DATE"], format="%Y-%m-%d")
df["ITEM_NAME"] = df["ITEM_NAME"].str.removeprefix("'HAPPIPPANG")

df["ITEM_NAME"] = df["ITEM_NAME"].apply(slugify)
df["STORE_NAME"] = df["STORE_NAME"].str.removeprefix("'")
df["STORE_NAME"] = df["STORE_NAME"].apply(slugify)
df.rename(columns={"SALES_DATE": "ds", "SALES_QTY": "y"}, inplace=True)

models = {}
forecasts = {}

out_dir = Path("./forecasts")
out_dir.mkdir(exist_ok=True)

for (store, item), grp in df.groupby(["STORE_NAME", "ITEM_NAME"]):
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

print(f"Built {len(models)} item‑level forecasts.  Plots saved to {out_dir.resolve()}")

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

