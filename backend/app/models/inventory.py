from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from backend.apputils.db import Base

from .mixin import TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint(
            "store_id", "item_id", "date", name="uix_inventory_store_item_date"
        ),
        CheckConstraint("db >= 0", name="chk_db_nonneg"),
        CheckConstraint("pg >= 0", name="chk_pg_nonneg"),
        CheckConstraint("waste >= 0", name="chk_waste_nonneg"),
        CheckConstraint("rem >= 0", name="chk_rem_nonneg"),
        CheckConstraint("b0_end >= 0", name="chk_b0_nonneg"),
        CheckConstraint("b1_end >= 0", name="chk_b1_nonneg"),
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

    # daily movements
    db = Column(Integer, nullable=False, server_default=0)  # qty_in
    pg = Column(Integer, nullable=False, server_default=0)  # qty_out

    # derived (3-day shelf life FIFO)
    waste = Column(Integer, nullable=False, server_default=0)  # expired at end of day
    rem = Column(Integer, nullable=False, server_default=0)  # end-of-day live stock
    b0_end = Column(
        Integer, nullable=False, server_default=0
    )  # today's leftover (age 0)
    b1_end = Column(
        Integer, nullable=False, server_default=0
    )  # yesterday's leftover (age 1)
