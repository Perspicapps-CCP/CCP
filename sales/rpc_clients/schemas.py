import datetime
import uuid
from decimal import Decimal
from typing import List, Optional

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


class WarehouseSchema(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str


class DeliveryItemSchema(BaseModel):
    order_number: str
    order_address: str
    customer_phone_number: Optional[str]
    product_code: str
    product_name: str
    quantity: Optional[int]
    images: List[str]


class DeliverySchema(BaseModel):
    shipping_number: str
    license_plate: str
    diver_name: str
    warehouse: WarehouseSchema
    delivery_status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    orders: List[DeliveryItemSchema]


class ReserveStockItemSchema(BaseModel):
    product_id: uuid.UUID
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class ReserveStockSchema(BaseModel):
    """
    Schema for reserving stock.
    """

    order_number: int
    sale_id: uuid.UUID
    items: List[ReserveStockItemSchema]
    model_config = ConfigDict(from_attributes=True)


class PayloadAddressSchema(BaseModel):
    id: uuid.UUID
    street: str
    city: str
    state: str
    postal_code: str
    country: str


class PayloadSaleItemSchema(BaseModel):
    sales_item_id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int


class PayloadSaleSchema(BaseModel):
    sales_id: uuid.UUID
    order_number: int
    address: PayloadAddressSchema
    sales_items: List[PayloadSaleItemSchema]
