import uuid
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict


class ProductSchema(BaseModel):
    id: uuid.UUID
    images: List[str]
    product_code: str
    name: str
    price: Decimal
    model_config = ConfigDict(from_attributes=True)
