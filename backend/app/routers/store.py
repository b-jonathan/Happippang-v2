from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreOut
from app.utils.db import get_session

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("/", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
async def create_store(data: StoreCreate, db: AsyncSession = Depends(get_session)):
    row = Store(**data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Store))
    return res.scalars().all()


@router.get("/{store_id}", response_model=StoreOut)
async def get_store(store_id: int, db: AsyncSession = Depends(get_session)):
    row = await db.get(Store, store_id)
    if not row:
        raise HTTPException(404, "Store not found")
    return row


@router.put("/{store_id}", response_model=StoreOut)
async def update_store(
    store_id: int, data: StoreUpdate, db: AsyncSession = Depends(get_session)
):
    stmt = (
        update(Store)
        .where(Store.id == store_id)
        .values(**data.model_dump())
        .returning(Store)
    )
    res = await db.execute(stmt)
    await db.commit()
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Store not found")
    return row


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(store_id: int, db: AsyncSession = Depends(get_session)):
    res = await db.execute(delete(Store).where(Store.id == store_id))
    if res.rowcount == 0:
        raise HTTPException(404, "Store not found")
    await db.commit()
