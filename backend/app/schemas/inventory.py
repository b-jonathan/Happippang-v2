# app/schemas/inventory.py
from datetime import date
from pydantic import BaseModel


class InventoryBase(BaseModel):
    store_id: int
    item_id: int
    date: date
    in_qty: int = 0
    out_qty: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    in_qty: int | None = None
    out_qty: int | None = None


class InventoryOut(InventoryBase):
    id: int

    class Config:
        from_attributes = True
