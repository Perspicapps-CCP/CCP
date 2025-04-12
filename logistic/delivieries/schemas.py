# Fite to validate the data that is being sent and recieved to the API
import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel, field_validator


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class DeliveryItemResponseSchema(BaseModel):
    order_number: str
    order_address: str
    customer_phone_number: str
    product_code: str
    product_name: str
    quantity: int
    images: List[str]


class DeliveryCreateRequestSchema(BaseModel):
    delivery_date: datetime.date
    warehouse_id: uuid.UUID

    @field_validator('delivery_date', mode='before')
    def validate_date(cls, v):
        if isinstance(v, datetime.date):
            return v

        try:
            date_obj = datetime.datetime.strptime(v, "%Y-%m-%d").date()
            return date_obj
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        except TypeError:
            raise ValueError("Invalid date value provided")


class WarehouseSchema(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str


class DeliveryCreateResponseSchema(BaseModel):
    shipping_number: str
    licence_plate: str
    diver_name: str
    warehouse: WarehouseSchema
    delivery_status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]


class DeliveryDetailResponseSchema(DeliveryCreateResponseSchema):
    orders: List[DeliveryItemResponseSchema]
