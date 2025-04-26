import re
import urllib.parse
from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

only_strings = r'^[a-zA-Z0-9_ñÑ ]+$'


class WarehouseSchema(BaseModel):
    warehouse_name: str
    country: str
    state: str
    city: str
    street: str
    phone: Union[str, int] = Field(
        description="Phone number as string or integer"
    )

    @field_validator('phone')
    def validate_phone(cls, v):
        phone_str = str(v)
        if not phone_str.isdigit():
            raise HTTPException(
                status_code=400, detail="Phone must contain only digits"
            )

        if len(phone_str) < 7 or len(phone_str) > 10:
            raise HTTPException(
                status_code=400, detail="Phone must be between 7 and 10 digits"
            )

        return phone_str


class WarehouseCreateResponseSchema(WarehouseSchema):
    warehouse_id: UUID
    address: Optional[str] = None
    created_at: datetime


class WarehouseGetResponseSchema(BaseModel):
    warehouse_id: UUID
    warehouse_name: str
    country: str
    state: str
    city: str
    street: str
    address: Optional[str] = None
    phone: Union[str, int]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_update: datetime

    @model_validator(mode='before')
    def check_warehouse_empty(self) -> 'WarehouseGetResponseSchema':
        if self is None:
            raise HTTPException(
                status_code=404,
                detail="The warehouse with this id does not exist.",
            )
        return self


class GetRequest(BaseModel):
    id: Optional[str] = None

    @field_validator('id', mode='before')
    def validate_id_param(cls, v):
        if v is not None:
            try:
                UUID(v)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="The id parameter must be a valid UUID format",
                )
        return v


class FilterRequest(GetRequest):
    name: Optional[str] = None

    @field_validator('name', mode='before')
    def validate_name_param(cls, v):
        if v is not None:
            try:
                decoded_name = urllib.parse.unquote(v)
                if not re.match(only_strings, decoded_name):
                    raise HTTPException(
                        status_code=400,
                        detail="The name parameter had not a valid format value",
                    )
                return decoded_name
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="The name parameter had not a valid format value",
                )
        return v
