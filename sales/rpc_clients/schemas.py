import datetime
import uuid
from decimal import Decimal
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict


class AddressSchema(BaseModel):
    """
    Schema for the address associated with a stop.
    """

    id: uuid.UUID
    line: str
    neighborhood: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    username: str
    phone: Optional[str]
    id_type: Optional[str]
    identification: Optional[str]
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    address: Optional[AddressSchema]

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    id: uuid.UUID
    images: List[str]
    product_code: str
    name: str
    price: Decimal
    model_config = ConfigDict(from_attributes=True)


class UserAuthSchema(UserSchema):
    """
    Schema for the user authentication response.
    """

    is_active: bool
    is_seller: bool
    is_client: bool

    model_config = ConfigDict(from_attributes=True)
class PayloadSaleItemSchema(BaseModel):
    sales_item_id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID


class PayloadSaleSchema(BaseModel):
    sales_id: uuid.UUID
    order_number: int
    address_id: uuid.UUID
    sales_items: List[PayloadSaleItemSchema]


class DeliverySaleStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class DeliverySaleResponseSchema(BaseModel):
    sale_id: uuid.UUID
    status: DeliverySaleStatus
    message: str
