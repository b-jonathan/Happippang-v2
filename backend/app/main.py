import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import inventory_router, item_router, store_router, user_router

app = FastAPI(
    title="Happippang API",
    root_path=os.getenv("FASTAPI_ROOT_PATH", ""),  # <- key line
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health():
    return {"status": "OK"}


app.include_router(store_router)
app.include_router(item_router)
app.include_router(inventory_router)
app.include_router(user_router)
