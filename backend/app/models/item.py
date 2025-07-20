from sqlalchemy import Column, DateTime, Integer, String, Numeric, func
from app.utils.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .mixin import TimestampMixin


class Item(Base, TimestampMixin):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    cost = Column(Integer(), nullable=False)
