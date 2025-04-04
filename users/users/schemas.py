# Shcema for user data validation
import datetime
import re
import uuid
from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationInfo,
    field_validator,
)
from sqlalchemy.orm import Session

from . import crud
from .models import IdTypeEnum


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

    password: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """
        Validate the password for minimum length and special characters.

        Args:
            value (str): The password to validate.

        Returns:
            str: The validated password.

        Raises:
            ValueError: If the password does not meet the criteria.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError(
                "Password must contain at least one special character."
            )
        return value

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
    seller_ids: List[uuid.UUID]


class GetSellersResponseSchema(BaseModel):
    sellers: List[UserDetailSchema]
