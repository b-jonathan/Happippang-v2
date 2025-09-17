import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from backend.app.utils.db import Base

from .mixin import TimestampMixin


class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
