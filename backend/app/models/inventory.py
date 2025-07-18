import uuid
from sqlalchemy import Column, Date, ForeignKey, Integer, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base

class Inventory(Base):
    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint("date", "store_id", "item_id", name="uix_inventory_store_item_date"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)

    qty_in = Column(Integer, nullable=False)
    qty_out = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
