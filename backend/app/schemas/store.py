# app/schemas/store.py
from pydantic import BaseModel, Field
from uuid import UUID


class StoreBase(BaseModel):
    name: str
    type: str = Field(..., pattern="^[A-Za-z0-9_ -]+$")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(StoreBase):
    name: str | None = None
    type: str | None = None


class StoreOut(StoreBase):
    id: UUID

    class Config:
        from_attributes = True
