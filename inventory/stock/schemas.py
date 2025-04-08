# Fite to validate the data that is being sent and recieved to the API
import datetime
import uuid
from fastapi import HTTPException
from typing import List, Optional
from pydantic import BaseModel, field_validator


class DeliveryItemSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int


class DeliveryCreateSchema(BaseModel):
    purchase_id: uuid.UUID
    address_id: uuid.UUID
    user_id: uuid.UUID
    items: List[DeliveryItemSchema]


class DeliveryDetailSchema(DeliveryCreateSchema):
    id: uuid.UUID
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    delivery_date: Optional[datetime.datetime]


class StockResponseSchema(BaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int
    last_updated: datetime.datetime


class FilterRequest(BaseModel):
    product: Optional[uuid.UUID] = None
    warehouse: Optional[uuid.UUID] = None


class StockRequestSchema(BaseModel):
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int

    @field_validator('quantity', mode='before')
    def validate_quantity(cls, v):
        if v < 0:
            raise HTTPException(
                status_code=400, detail="The quantity cannot be negative"
            )
        return v


class OperationResponseSchema(BaseModel):
    operation_id: uuid.UUID
    warehouse_id: uuid.UUID
    processed_records: int
    successful_records: int
    failed_records: int
    created_at: datetime.datetime
