from pydantic import BaseModel
from uuid import UUID


class ItemBase(BaseModel):
    name: str
    category: str
    cost: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    cost: int | None = None


class ItemOut(ItemBase):
    id: UUID

    class Config:
        from_attributes = True
