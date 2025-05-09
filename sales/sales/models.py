import enum
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


class SaleStatusEnum(str, enum.Enum):
    """Enum for sale status."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class Sale(Base):
    __tablename__ = "sales"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), nullable=True)
    client_id = Column(UUID(as_uuid=True), nullable=False)
    order_number = Column(
        Integer,
        Sequence("order_number_seq", start=1, increment=1),
        unique=True,
        nullable=False,
    )
    status = Column(
        String(100),
        nullable=False,
        default=SaleStatusEnum.CREATED,
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
    deliveries = relationship(
        "SaleDelivery",
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


class SaleDelivery(Base):
    __tablename__ = "sales_delivery"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False
    )
    delivery_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    sale = relationship(
        "Sale",
        back_populates="deliveries",
    )
