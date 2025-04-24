import uuid
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict

from warehouse import schemas as warehouse_schemas


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


class GetWarehousesResponseSchema(BaseModel):
    warehouses: list[warehouse_schemas.WarehouseGetResponseSchema]
    model_config = ConfigDict(from_attributes=True)
