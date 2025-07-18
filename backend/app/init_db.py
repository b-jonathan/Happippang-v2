import asyncio
from db import async_engine, Base
import models

# Not used but avoid linting error lol
_ = models

async def init_models():
    print("Using DB URL:", async_engine.url)
    print("Creating tables:", Base.metadata.tables.keys())

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_models())



