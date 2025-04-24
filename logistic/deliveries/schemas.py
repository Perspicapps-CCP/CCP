# Fite to validate the data that is being sent and recieved to the API
import datetime
from enum import Enum
import uuid
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class DeliveryItemGetResponseSchema(BaseModel):
    order_number: str
    order_address: str
    customer_phone_number: Optional[str] = "01234456789"
    product_code: str
    product_name: str
    quantity: Optional[int] = 1
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
    license_plate: str
    diver_name: str
    warehouse: WarehouseSchema
    delivery_status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]


class DeliveryDetailGetResponseSchema(DeliveryCreateResponseSchema):
    orders: List[DeliveryItemGetResponseSchema]


class DriverCreateSchema(BaseModel):
    driver_name: str
    license_plate: str
    phone_number: Union[str, int] = Field(
        description="Phone number as string or integer"
    )

    @field_validator('phone_number')
    def validate_phone(cls, v):
        phone_str = str(v)
        if not phone_str.isdigit():
            raise Exception(
                status_code=400, detail="Phone must contain only digits"
            )

        if len(phone_str) < 7 or len(phone_str) > 10:
            raise Exception(
                status_code=400, detail="Phone must be between 7 and 10 digits"
            )

        return phone_str


class PayloadSaleItemSchema(BaseModel):
    sales_item_id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID


class PayloadSaleSchema(BaseModel):
    sales_id: uuid.UUID
    order_number: int
    address_id: uuid.UUID
    address: str
    sales_items: List[PayloadSaleItemSchema]


class DeliverySaleStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class DeliverySaleResponseSchema(BaseModel):
    sale_id: uuid.UUID
    status: DeliverySaleStatus
    message: str
