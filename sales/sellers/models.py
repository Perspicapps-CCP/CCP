import datetime
import uuid

from sqlalchemy import UUID, Column, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from database import Base

from .constants import VISITED_RECENTLY_HOURS


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
        UniqueConstraint("client_id", "seller_id", name="client_sellet"),
    )

    @property
    def was_visited_recently(self) -> bool:
        """
        Determines if the client was visited recently based on the last visited timestamp.
        Returns:
            bool: True if the client was visited within the time frame defined by
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
