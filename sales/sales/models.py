import enum
import json
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
    Enum,
    JSON,
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


class OutboxMessageType(enum.Enum):
    SALES_ORDER = "SALES_ORDER"


class OutboxStatus(enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class Outbox(Base):
    __tablename__ = "outbox"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_type = Column(
        Enum(OutboxMessageType),
        nullable=False,
        default=OutboxMessageType.SALES_ORDER,
    )
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(OutboxStatus), nullable=False, default=OutboxStatus.PENDING
    )
    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    attempt_count = Column(Integer, nullable=False, default=0)

    def set_payload(self, payload_dict):
        self.payload = json.dumps(payload_dict)

    def get_payload(self):
        return json.loads(self.payload) if self.payload else {}
