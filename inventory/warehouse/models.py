import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from stock.models import Stock, Operation


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=False)
    latitude = Column(Numeric(precision=10, scale=7), nullable=True)
    longitude = Column(Numeric(precision=10, scale=7), nullable=True)
    warehouses = relationship("Warehouse", back_populates="address")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    address_id = Column(
        UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False
    )
    phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    address = relationship("Address", back_populates="warehouses")
    stocks = relationship(Stock, back_populates="warehouse")
    operations = relationship(Operation, back_populates="warehouse")

    def __repr__(self):
        return f"<Warehouse(id={self.id}, name={self.name}, address_id={self.address_id}, phone={self.phone})>"
