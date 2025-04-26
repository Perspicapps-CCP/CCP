import uuid
from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict


class ManufacturerSchema(BaseModel):
    id: uuid.UUID
    manufacturer_name: str
    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    id: uuid.UUID
    images: List[str]
    product_code: str
    name: str
    price: Decimal
    manufacturer: ManufacturerSchema
    model_config = ConfigDict(from_attributes=True)


class WarehouseSchema(BaseModel):
    warehouse_id: uuid.UUID
    warehouse_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Union[str, int]


class GetWarehousesResponseSchema(BaseModel):
    warehouses: list[WarehouseSchema]
    model_config = ConfigDict(from_attributes=True)
