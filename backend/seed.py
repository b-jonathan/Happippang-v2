import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.appmodels import Item, Store
from backend.apputils.db import get_async_engine


async def seed():
    engine = get_async_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        stmt = select(func.count()).select_from(Item)
        item_count = await session.scalar(stmt)
        stmt = select(func.count()).select_from(Store)
        stores_count = await session.scalar(stmt)
        added = []
        if item_count <= 0:
            items = [
                {"name": "ORI", "category": "Bluder", "cost": 5000},
                {"name": "Choco", "category": "Bluder", "cost": 7000},
                {"name": "Cheese", "category": "Bluder", "cost": 7000},
                {"name": "ChocoCheese", "category": "Bluder", "cost": 7000},
                {"name": "Smoked Beef", "category": "Bluder", "cost": 7000},
                {"name": "Abon", "category": "Bluder", "cost": 7000},
                {"name": "Bluberry", "category": "Bluder", "cost": 7000},
                {"name": "Bunny", "category": "SC", "cost": 3000},
                {"name": "Bear", "category": "SC", "cost": 3000},
                {"name": "Cat", "category": "SC", "cost": 3000},
                {"name": "Cok", "category": "Wassant", "cost": 17500},
                {"name": "Keju", "category": "Wassant", "cost": 17500},
                {"name": "Mix", "category": "Wassant", "cost": 17500},
                {"name": "Kotak", "category": "Milky", "cost": 18000},
                {"name": "Bunny", "category": "Milky", "cost": 12000},
                {"name": "Cat.Duo", "category": "Milky", "cost": 12000},
                {"name": "Bear", "category": "Milky", "cost": 12000},
                {"name": "meses", "category": "LJ", "cost": 5250},
                {"name": "cheese", "category": "LJ", "cost": 6000},
                {"name": "rainbow", "category": "LJ", "cost": 5500},
                {"name": "duo", "category": "LJ", "cost": 6500},
                {"name": "Manis Kotak", "category": "Bagelen", "cost": 10000},
                {"name": "Manis Cat", "category": "Bagelen", "cost": 3000},
                {"name": "Manis Bunny", "category": "Bagelen", "cost": 3000},
                {"name": "Manis Bear", "category": "Bagelen", "cost": 3000},
                {"name": "Garlic Kotak", "category": "Bagelen", "cost": 10000},
                {"name": "Garlic Cat", "category": "Bagelen", "cost": 3000},
                {"name": "Garlic Bunny", "category": "Bagelen", "cost": 3000},
                {"name": "Garlic Bear", "category": "Bagelen", "cost": 3000},
                {"name": "Cok", "category": "RJ", "cost": 5000},
                {"name": "Cokju", "category": "RJ", "cost": 5000},
                {"name": "Piscok", "category": "RJ", "cost": 6000},
                {"name": "Abon", "category": "RJ", "cost": 6000},
                {"name": "Sosis", "category": "RJ", "cost": 6000},
                {"name": "Spicy", "category": "RJ", "cost": 8000},
                {"name": "Baso", "category": "RJ", "cost": 6000},
                {"name": "Cheese Bomb", "category": "RJ", "cost": 8000},
                {"name": "Butter Roll", "category": "GL", "cost": 14000},
                {"name": "Roti Sisir Mocha", "category": "GL", "cost": 8000},
                {"name": "Roti Sisir Cheese", "category": "GL", "cost": 8000},
            ]
            session.add_all([Item(**item) for item in items])
            added.append("items")
        if stores_count <= 0:
            stores = [
                {"name": "Carrefour CBD Pluit", "type": "Hero"},
                {"name": "Central Park", "type": "Hero"},
                {"name": "Kota Kasablanka", "type": "Hero"},
            ]
            session.add_all([Store(**store) for store in stores])
            added.append("stores")
        if len(added) > 0:
            print(f"Seeded: {', '.join(added)}")
            await session.commit()
        else:
            print("No seeding needed, database already has data.")

    await engine.dispose()  # move outside the `async with` block


if __name__ == "__main__":
    asyncio.run(seed())
