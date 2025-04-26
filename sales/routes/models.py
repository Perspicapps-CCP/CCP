import uuid

from sqlalchemy import (
    UUID,
    Column,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Route(Base):
    """
    Represents a delivery route.
    """

    __tablename__ = "routes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    stops = relationship("Stop", back_populates="route")
    __table_args__ = (
        UniqueConstraint("seller_id", "date", name="seller_date_unique"),
    )


class Stop(Base):
    """
    Represents a stop in a route.
    """

    __tablename__ = "stops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(
        UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False
    )
    client_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    route = relationship("Route", back_populates="stops")
