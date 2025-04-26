import enum
import uuid

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class RoleEnum(str, enum.Enum):
    """
    RoleEnum is an enumeration that defines the different roles available
    in the system.
    Attributes:
        STAFF (str): Represents a staff member role.
        SELLER (str): Represents a seller role.
        CLIENT (str): Represents a buyer role.
    """

    STAFF = "STAFF"
    SELLER = "SELLER"
    CLIENT = "CLIENT"


class IdTypeEnum(str, enum.Enum):
    """
    IdTypeEnum is an enumeration that represents
      different types of identification.
    Attributes:
      CC (str): Represents (Citizen ID).
      NIT (str): Represents (Tax Identification Number).
      OTHER (str): Represents any other type of identification.
    """

    CC = "CC"
    NIT = "NIT"
    OTHER = "OTHER"


class User(Base):
    """
    User Model
    Represents a user in the system.
    Attributes:
        id (int): Primary key, unique identifier for the user.
        username (str): Unique username for the user, required.
        hashed_password (str): Hashed password for the user, required.
        full_name (str): Full name of the user, optional.
        is_active (bool): Indicates whether the user is active.
          Defaults to True.
        role (RoleEnum): Role of the user in the system, required.
        created_at (datetime): Timestamp when the user was created.
          Defaults to the current time.
        updated_at (datetime): Timestamp when the user was last updated.
          Automatically updated.
        email (str): Unique email address of the user, optional.
        phone (str): Unique phone number of the user, optional.
          Unformatted.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(256))
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    email = Column(String(256), unique=True, nullable=True)
    phone = Column(String(256), unique=True, nullable=True)
    id_type = Column(Enum(IdTypeEnum), nullable=True)
    identification = Column(String(256), nullable=True)
    address = relationship("Address", backref="user", uselist=False)


class Address(Base):
    """
    Represents an address associated with an User.
    """

    __tablename__ = "addresses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    line = Column(String, nullable=False)
    neighborhood = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    __table_args__ = (UniqueConstraint("user_id"),)
