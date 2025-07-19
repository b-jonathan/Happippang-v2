# app/schemas/store.py
from pydantic import BaseModel, Field
from uuid import UUID


# ✅ shared fields
class StoreBase(BaseModel):
    name: str
    type: str = Field(..., pattern="^[A-Za-z0-9_ -]+$")


# ✅ for POST
class StoreCreate(StoreBase):
    pass


# ✅ for PUT/PATCH
class StoreUpdate(StoreBase):
    pass


# ✅ for responses
class StoreOut(StoreBase):
    id: UUID

    class Config:
        from_attributes = True
