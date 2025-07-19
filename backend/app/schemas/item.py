# app/schemas/item.py
from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    category: str
    cost: int  # cents


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    cost: int | None = None


class ItemOut(ItemBase):
    id: int

    class Config:
        from_attributes = True
