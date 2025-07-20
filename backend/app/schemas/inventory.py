from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date


class InventoryLine(BaseModel):
    item_id: UUID
    db: int = Field(ge=0)
    pg: int = Field(ge=0)


class InventoryBulkCreate(BaseModel):
    store_id: UUID
    date: date
    items: list[InventoryLine]


class InventoryBase(InventoryLine):
    store_id: UUID
    date: date


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    db: int | None = None
    pg: int | None = None


class InventoryOut(InventoryBase):
    id: UUID

    class Config:
        from_attributes = True
