import uuid

from sqlalchemy import UUID, Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class SalesPlan(Base):
    __tablename__ = "sales_plan"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    goal = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    sellers = relationship(
        "SellerInPlan",
        back_populates="plan",
    )


class SellerInPlan(Base):
    __tablename__ = "seller_in_plan"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), nullable=False)
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("sales_plan.id"), nullable=False
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    plan = relationship(
        "SalesPlan",
        back_populates="sellers",
    )
