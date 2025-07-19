# from datetime import date
# from typing import Dict, List
from fastapi import FastAPI, Query
from .routers import store_router  # , item_router, inventory_router


app = FastAPI()


@app.get("/")
async def health():
    return {"status": "OK"}


app = FastAPI(title="Happippang API")

app.include_router(store_router)
# app.include_router(item_router)
# app.include_router(inventory_router)
