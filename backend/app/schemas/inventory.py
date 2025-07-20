from pydantic import BaseModel
from uuid import UUID
from datetime import date


class InventoryBase(BaseModel):
    store_id: UUID
    item_id: UUID
    date: date
    db: int = 0
    pg: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    db: int | None = None
    pg: int | None = None


class InventoryOut(InventoryBase):
    id: UUID

    class Config:
        from_attributes = True
