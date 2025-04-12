import enum
import uuid

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class DeliverStatus(str, enum.Enum):
    CREATED = "CREATED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"))
    warehouse_id = Column(UUID(as_uuid=True), nullable=False)
    delivery_date = Column(DateTime(timezone=True))
    status = Column(Enum(DeliverStatus), default=DeliverStatus.CREATED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    items = relationship("DeliveryItem", back_populates="delivery")
    driver = relationship("Driver", back_populates="deliveries")


class DeliveryItem(Base):
    __tablename__ = "delivery_items"
    __table_args__ = (
        UniqueConstraint(
            "delivery_id", "order_number", "product_id", "warehouse_id", name="uix_delivery_product"
        ),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"))
    warehouse_id = Column(UUID(as_uuid=True), nullable=False)
    order_number = Column(UUID(as_uuid=True), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivery = relationship("Delivery", back_populates="items")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    licence_plate = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=False)
    is_available = Column(Boolean, nullable=False, default=1)
    deliveries = relationship("Delivery", back_populates="driver")

