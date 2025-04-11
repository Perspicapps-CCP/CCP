from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from rpc_clients.schemas import ProductSchema, SellerSchema


class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str

    model_config = ConfigDict(from_attributes=True)


class SaleItemSchema(BaseModel):
    id: UUID
    product: ProductSchema
    quantity: int
    unit_price: Decimal
    total_value: Decimal
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class SaleDetailSchema(BaseModel):
    id: UUID
    seller: SellerSchema
    order_number: int
    address: AddressSchema
    total_value: Decimal
    currency: str
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[SaleItemSchema]

    model_config = ConfigDict(from_attributes=True)


class ListSalesQueryParamsSchema(BaseModel):
    order_number: Optional[int] = None
    seller_name: Optional[str] = None
    seller_id: Optional[List[UUID]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
