# Fite to validate the data that is being sent and recieved to the API
import datetime
import uuid
from typing import List, Optional

from pydantic import BaseModel


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class DeliveryItemSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int


class DeliveryCreateSchema(BaseModel):
    purchase_id: uuid.UUID
    address_id: uuid.UUID
    user_id: uuid.UUID
    items: List[DeliveryItemSchema]


class DeliveryItemResponseSchema(DeliveryItemSchema):
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class DeliveryDetailSchema(DeliveryCreateSchema):
    id: uuid.UUID
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    delivery_date: Optional[datetime.datetime]
    items: List[DeliveryItemResponseSchema]

    class Config:
        orm_mode = True
