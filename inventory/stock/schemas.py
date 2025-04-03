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
    product: Optional[str] = None
    warehouse: Optional[str] = None

    @field_validator('product', mode='before')
    def validate_product_param(cls, v):
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="The product parameter must be a valid UUID format",
                )
        return v

    @field_validator('warehouse', mode='before')
    def validate_warehouse_param(cls, v):
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="The warehouse parameter must be a valid UUID format",
                )
        return v


class StockRequestSchema(BaseModel):
    warehouse_id: str
    product_id: str
    quantity: int

    @field_validator('warehouse_id', 'product_id', mode='before')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="The warehouse_id and product_id must be a valid UUID",
            )
        return v

    @field_validator('quantity', mode='before')
    def validate_quantity(cls, v):
        if v < 0:
            raise HTTPException(
                status_code=400, detail="The quantity cannot be negative"
            )
        return v


class WarehouseIdSchema(BaseModel):
    warehouse_id: str

    @field_validator('warehouse_id')
    def validate_warehouse_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("The warehouse_id must be a valid UUID")
        return v


class OperationResponseSchema(BaseModel):
    operation_id: uuid.UUID
    warehouse_id: uuid.UUID
    processed_records: int
    successful_records: int
    failed_records: int
    created_at: datetime.datetime
