from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate, ItemOut
from app.utils.db import get_session

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_session)):
    row = Item(**data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/", response_model=list[ItemOut])
async def list_items(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Item))
    return res.scalars().all()


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: UUID, db: AsyncSession = Depends(get_session)):
    row = await db.get(Item, item_id)
    if not row:
        raise HTTPException(404, "Item not found")
    return row


@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: UUID, data: ItemUpdate, db: AsyncSession = Depends(get_session)
):
    stmt = (
        update(Item)
        .where(Item.id == item_id)
        .values(**data.model_dump(exclude_none=True))
        .returning(Item)
    )
    res = await db.execute(stmt)
    await db.commit()
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Item not found")
    return row


@router.delete("/{item_id}", response_model=ItemOut)
async def delete_item(item_id: UUID, db: AsyncSession = Depends(get_session)):
    stmt = delete(Item).where(Item.id == item_id).returning(Item)
    res = await db.execute(stmt)
    row = res.scalar_one_or_none()
    await db.commit()
    if not row:
        raise HTTPException(404, "Item not found")
    return row
