import enum
import uuid

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, String
from sqlalchemy.sql import func

from database import Base


class RoleEnum(str, enum.Enum):
    """
    RoleEnum is an enumeration that defines the different roles available
    in the system.
    Attributes:
        STAFF (str): Represents a staff member role.
        SELLER (str): Represents a seller role.
        BUYER (str): Represents a buyer role.
    """

    STAFF = "STAFF"
    SELLER = "SELLER"
    BUYER = "BUYER"


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
        phone_number (str): Unique phone number of the user, optional.
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
    phone_number = Column(String(256), unique=True, nullable=True)
