# Shcema for user data validation
import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class ErrorResponseSchema(BaseModel):
    detail: str


class UserBaseSchema(BaseModel):
    username: str
    full_name: str
    email: str
    phone_number: str | None


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
