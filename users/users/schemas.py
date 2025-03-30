# Shcema for user data validation
import datetime
import re
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ErrorResponseSchema(BaseModel):
    detail: str


class UserBaseSchema(BaseModel):
    username: str = Field(..., max_length=256)
    full_name: str = Field(..., max_length=256)
    email: EmailStr = Field(..., max_length=256)
    phone_number: str | None = Field(..., max_length=256)


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


class CreateStaffSchema(UserBaseSchema):
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
