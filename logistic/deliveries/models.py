import enum
import uuid
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
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
    __table_args__ = (
        UniqueConstraint(
            "driver_id",
            "delivery_date",
            name="uix_driver_delivery_date",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(
        UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True
    )
    warehouse_id = Column(UUID(as_uuid=True), nullable=False)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(DeliverStatus), default=DeliverStatus.CREATED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    driver = relationship("Driver", back_populates="deliveries")
    stops = relationship("DeliveryStop", back_populates="delivery")


class DeliveryStop(Base):
    __tablename__ = "delivery_stops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sales_id = Column(UUID(as_uuid=True), nullable=False)
    order_number = Column(Integer, nullable=False)
    address_id = Column(
        UUID(as_uuid=True),
        ForeignKey("delivery_address.address_id"),
        nullable=False,
    )
    delivery_id = Column(
        UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivery = relationship("Delivery", back_populates="stops")
    items = relationship("DeliveryItem", back_populates="delivery_stop")
    address = relationship("DeliveryAddress", back_populates="delivery_stops")


class DeliveryItem(Base):
    __tablename__ = "delivery_items"
    __table_args__ = (
        UniqueConstraint(
            "sales_id",
            "order_number",
            "product_id",
            name="uix_delivery_product",
        ),
    )
    sales_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    order_number = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), nullable=False)
    delivery_stop_id = Column(
        UUID(as_uuid=True), ForeignKey("delivery_stops.id"), nullable=False
    )
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivery_stop = relationship("DeliveryStop", back_populates="items")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    license_plate = Column(String(20), nullable=False)
    phone_number = Column(String(20), nullable=False)
    is_available = Column(Boolean, nullable=False, default=1)
    deliveries = relationship("Delivery", back_populates="driver")


class DeliveryAddress(Base):
    __tablename__ = "delivery_address"

    address_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivery_stops = relationship("DeliveryStop", back_populates="address")
