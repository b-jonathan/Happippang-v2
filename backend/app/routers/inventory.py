from __future__ import annotations

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db import get_session
from backend.app.schemas.inventory import InventoryBulkCreate, InventoryOut
from backend.app.services.inventory_service import bulk_upsert_inventory

router = APIRouter(prefix="/inventories", tags=["inventories"])


@router.post(
    "/bulk",
    response_model=List[InventoryOut],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_inventories(
    payload: InventoryBulkCreate,
    session: AsyncSession = Depends(get_session),
    mode: Optional[Literal["propagate", "freeze"]] = None,  # query param override
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="items list cannot be empty")

    rows = await bulk_upsert_inventory(session, payload, mode=mode)
    if not rows:
        raise HTTPException(status_code=400, detail="all rows were zero")
    return rows
