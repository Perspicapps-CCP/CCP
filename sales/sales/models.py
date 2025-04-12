import uuid

from sqlalchemy import (
    DECIMAL,
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Sale(Base):
    __tablename__ = "sales"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), nullable=False)
    order_number = Column(
        Integer,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    address_id = Column(UUID(as_uuid=True), nullable=False)
    total_value = Column(DECIMAL(precision=20, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    items = relationship(
        "SaleItem",
        back_populates="sale",
    )


class SaleItem(Base):
    __tablename__ = "sales_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False
    )
    product_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(precision=20, scale=2), nullable=False)
    total_value = Column(DECIMAL(precision=20, scale=2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    sale = relationship(
        "Sale",
        back_populates="items",
    )
