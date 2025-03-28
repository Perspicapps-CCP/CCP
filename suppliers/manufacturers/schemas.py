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
    manufacturer_name: str  = Field(..., min_length=1) 
    identification_type: str  = Field(..., min_length=1) 
    identification_number: str  = Field(..., min_length=1) 
    address: str  = Field(..., min_length=1) 
    contact_phone: str  = Field(..., min_length=1) 
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
