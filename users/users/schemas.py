# Shcema for user data validation
import datetime
import uuid
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)
from sqlalchemy.orm import Session

from . import crud
from .models import IdTypeEnum, RoleEnum


class AddressSchema(BaseModel):
    """
    Schema for the address associated with a stop.
    """

    id: uuid.UUID
    line: str
    neighborhood: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class ErrorResponseSchema(BaseModel):
    detail: str


class UserBaseSchema(BaseModel):
    username: str = Field(..., max_length=256, min_length=3)
    full_name: str = Field(..., max_length=256)
    email: EmailStr = Field(..., max_length=256)
    phone: str | None = Field(..., max_length=256, min_length=10)
    id_type: IdTypeEnum | None = Field(..., max_length=256)
    identification: str | None = Field(..., max_length=256)


class UserDetailSchema(UserBaseSchema):
    id: uuid.UUID
    role: str
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    is_active: bool
    address: Optional[AddressSchema]

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime.datetime
    user: UserDetailSchema


class CreateSellerSchema(UserBaseSchema):

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username")
    def validate_username(cls, value: str, info: ValidationInfo) -> str:
        """
        Validate the username for minimum length.

        Args:
            value (str): The username to validate.

        Returns:
            str: The validated username.

        Raises:
            ValueError: If the username does not meet the criteria.
        """
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        db: Session = info.context.get("db")
        if crud.is_username_taken(db, value):
            raise ValueError("Username is already taken.")
        return value

    @field_validator("email")
    def validate_email(cls, value: str, info: ValidationInfo) -> str:
        """
        Validate the email for format and uniqueness.

        Args:
            value (str): The email to validate.

        Returns:
            str: The validated email.

        Raises:
            ValueError: If the email does not meet the criteria.
        """
        db: Session = info.context.get("db")
        if crud.is_email_taken(db, value):
            raise ValueError("Email is already taken.")
        return value

    @field_validator("phone")
    def validate_phone(cls, value: str, info: ValidationInfo) -> str:
        """
        Validate the phone number for format and uniqueness.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            ValueError: If the phone number does not meet the criteria.
        """
        db: Session = info.context.get("db")
        if crud.is_phone_taken(db, value):
            raise ValueError("Phone number is already taken.")
        return value


class GetSellersSchema(BaseModel):
    seller_ids: Optional[List[uuid.UUID]]


class GetSellersResponseSchema(BaseModel):
    sellers: List[UserDetailSchema]


class GetClientsSchema(BaseModel):
    client_ids: Optional[List[uuid.UUID]]


class GetClientsResponseSchema(BaseModel):
    clients: List[UserDetailSchema]


class AuthSchema(BaseModel):
    """
    Schema for authentication data.
    """

    bearer_token: str

    model_config = ConfigDict(from_attributes=True)


class UserAuthDetailSchema(UserDetailSchema):
    is_active: bool

    @computed_field
    @property
    def is_seller(self) -> bool:
        """
        Check if the user is a seller.

        Returns:
            bool: True if the user is a seller, False otherwise.
        """
        return self.role == RoleEnum.SELLER

    @computed_field
    @property
    def is_client(self) -> bool:
        """
        Check if the user is a client.

        Returns:
            bool: True if the user is a client, False otherwise.
        """
        return self.role == RoleEnum.CLIENT


class AuthResponseSchema(BaseModel):
    """
    Schema for authentication response data.
    """

    user: Optional[UserAuthDetailSchema]

    model_config = ConfigDict(from_attributes=True)
