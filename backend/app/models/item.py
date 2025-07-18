from sqlalchemy import Column, DateTime, String, Numeric, func
from app.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    cost = Column(Numeric(10, 2), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)