import uuid
import enum
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UUID,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from database import Base


class OperationType(enum.Enum):
    LOAD = 0
    UNLOAD = 1


class Stock(Base):
    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "warehouse_id", name="unique_product_by_warehouse"
        ),
    )
    warehouse_id = Column(
        UUID(as_uuid=True), ForeignKey("warehouses.id"), primary_key=True
    )
    product_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    warehouse = relationship("Warehouse", back_populates="stocks")

    def __repr__(self):
        return f"<Stock(warehouse_id={self.warehouse_id}, product_id={self.product_id}, quantity={self.quantity})>"


class Operation(Base):
    __tablename__ = "operations"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4()
    )
    file_name = Column(String, nullable=False)
    operation_type = Column(
        Enum(OperationType), nullable=False, default=OperationType.LOAD
    )
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"))
    processed_records = Column(Integer, nullable=False, default=0)
    successful_records = Column(Integer, nullable=False, default=0)
    failed_records = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    warehouse = relationship("Warehouse", back_populates="operations")

    def __repr__(self):
        return f"<Operation(id={self.id}, file_name={self.file_name}, operation_type={self.operation_type}, processed_records={self.processed_records}, successful_records={self.successful_records}, failed_records={self.failed_records})>"


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
