import uuid
from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from app.utils.db import Base
from .mixin import TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint(
            "date", "store_id", "item_id", name="uix_inventory_store_item_date"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)

    store_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    qty_in = Column(Integer, nullable=False)
    qty_out = Column(Integer, nullable=False)
