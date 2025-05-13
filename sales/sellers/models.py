import datetime
import enum
import uuid

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    UniqueConstraint,
    String,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

from .constants import VISITED_RECENTLY_HOURS


class VideoStatusEnum(str, enum.Enum):
    """Enum for video status."""

    PENDING = "PENDING"
    ANALISYS_GENERATED = "ANALISYS_GENERATED"
    RECOMENDATIONS_GENERATED = "RECOMENDATIONS_GENERATED"


class ClientForSeller(Base):
    """
    Represents the assignment of a client to a seller.
    """

    __tablename__ = "client_for_seller"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), nullable=False)
    seller_id = Column(UUID(as_uuid=True), nullable=False)
    last_visited = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("client_id", "seller_id", name="client_seller"),
    )

    @property
    def was_visited_recently(self) -> bool:
        """
        Determines if the client was visited recently based on the last
          visited timestamp.
        Returns:
            bool: True if the client was visited within the
            time frame defined by
                  VISITED_RECENTLY_HOURS, False otherwise.
        """

        return (
            bool(self.last_visited)
            and (
                self.last_visited
                + datetime.timedelta(hours=VISITED_RECENTLY_HOURS)
            )
            >= datetime.datetime.now()
        )


class ClientVisit(Base):
    __tablename__ = "client_visit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True))
    description = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    attachments = relationship("ClientAttachment", back_populates="visit")


class ClientAttachment(Base):
    __tablename__ = "client_attachment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_file = Column(String(500), nullable=False)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("client_visit.id"))
    visit = relationship("ClientVisit", back_populates="attachments")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClientVideo(Base):
    __tablename__ = "client_video"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True))
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    recomendations = Column(String(3000), nullable=True)
    url = Column(String(500), nullable=False)
    status = Column(
        Enum(VideoStatusEnum),
        default=VideoStatusEnum.PENDING,
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
