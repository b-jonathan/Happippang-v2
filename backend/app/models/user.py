from sqlalchemy import Column, String
from app.utils.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .mixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
