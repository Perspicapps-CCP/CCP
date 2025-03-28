# Fite to validate the data that is being sent and recieved to the API
import datetime
import uuid
from typing import Optional
from . import models

from pydantic import BaseModel, field_validator, ConfigDict, Field, EmailStr


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class ManufacturerItemSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int


class ManufacturerCreateSchema(BaseModel):
    manufacturer_name: str 
    identification_type: str
    identification_number: str 
    address: str 
    contact_phone: str 
    email: EmailStr        
    @field_validator("identification_type")
    @classmethod
    def validate_identification_type(cls, value):
        try:
            return models.IdentificationType(value)
        except ValueError:
            raise ValueError(f"El tipo de identificación '{value}' no es válido.")


class DeliveryItemResponseSchema(ManufacturerItemSchema):
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)

class ManufacturerDetailSchema(ManufacturerCreateSchema):
    id: uuid.UUID   
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)
