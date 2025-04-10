import uuid
from decimal import Decimal
from typing import List

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
