from __future__ import annotations

from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryItemIn(BaseModel):
    item_id: UUID
    db: int = Field(0, ge=0)
    pg: int = Field(0, ge=0)


class InventoryBulkCreate(BaseModel):
    store_id: UUID
    date: date
    items: List[InventoryItemIn]
    # Optional: request-time behavior; can also be a query param
    mode: Literal["propagate", "freeze"] = "propagate"


class InventoryOut(BaseModel):
    id: UUID
    store_id: UUID
    item_id: UUID
    date: date
    db: int
    pg: int
    waste: int
    rem: int
    b0_end: int
    b1_end: int

    class Config:  # Pydantic v1
        orm_mode = True

    # For Pydantic v2, use:
    # model_config = {"from_attributes": True}
