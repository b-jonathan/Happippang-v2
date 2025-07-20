from fastapi import FastAPI, Query
from .routers import store_router, item_router, inventory_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Happippang API")


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
