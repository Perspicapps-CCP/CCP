import uuid

from sqlalchemy import UUID, Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stocks = relationship("Stock", back_populates="warehouse")
    operations = relationship("Operation", back_populates="warehouse")

    def __repr__(self):
        return f"<Warehouse(id={self.id}, name={self.name}, country={self.country}, city={self.city}, address={self.address}, phone={self.phone})>"
