from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    username: str


class UserCreate(User):
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(User):
    id: UUID

    class Config:
        from_attributes = True
