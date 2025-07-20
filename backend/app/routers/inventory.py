from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.inventory import Inventory
from app.schemas.inventory import (
    InventoryBulkCreate,
    InventoryCreate,
    InventoryUpdate,
    InventoryOut,
)
from app.utils.db import get_session

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    data: InventoryCreate, db: AsyncSession = Depends(get_session)
):
    row = Inventory(**data.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.post(
    "/bulk",
    response_model=list[InventoryOut],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_inventory(
    payload: InventoryBulkCreate,
    db: AsyncSession = Depends(get_session),
):
    if not payload.items:
        raise HTTPException(400, "items list cannot be empty")

    # build the list of dicts for INSERT
    rows = [
        {
            "store_id": payload.store_id,
            "date": payload.date,
            "item_id": line.item_id,
            "db": line.db,  # `db` → `in_qty`
            "pg": line.pg,  # `pg` → `out_qty`
        }
        for line in payload.items
        # optionally skip lines where both are zero:
        if line.db or line.pg
    ]

    if not rows:
        raise HTTPException(400, "all rows were zero")

    # one-shot INSERT ... RETURNING
    stmt = insert(Inventory).returning(Inventory)
    result = await db.execute(stmt, rows)
    await db.commit()

    return result.scalars().all()


@router.get("/", response_model=list[InventoryOut])
async def list_inventory(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Inventory))
    return res.scalars().all()


@router.get("/{inv_id}", response_model=InventoryOut)
async def get_inventory(inv_id: UUID, db: AsyncSession = Depends(get_session)):
    row = await db.get(Inventory, inv_id)
    if not row:
        raise HTTPException(404, "Inventory row not found")
    return row


@router.put("/{inv_id}", response_model=InventoryOut)
async def update_inventory(
    inv_id: UUID, data: InventoryUpdate, db: AsyncSession = Depends(get_session)
):
    stmt = (
        update(Inventory)
        .where(Inventory.id == inv_id)
        .values(**data.model_dump(exclude_none=True))
        .returning(Inventory)
    )
    res = await db.execute(stmt)
    await db.commit()
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Inventory row not found")
    return row


@router.delete("/{inv_id}", response_model=InventoryOut)
async def delete_inventory(inv_id: UUID, db: AsyncSession = Depends(get_session)):
    stmt = delete(Inventory).where(Inventory.id == inv_id).returning(Inventory)
    res = await db.execute(stmt)
    row = res.scalar_one_or_none()
    await db.commit()
    if not row:
        raise HTTPException(404, "Inventory row not found")
    return row
