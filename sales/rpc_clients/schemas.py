import datetime
import uuid
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SellerSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    username: str
    phone: str
    id_type: str
    identification: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(BaseModel):
    id: uuid.UUID
    images: List[str]
    product_code: str
    name: str
    price: Decimal
    model_config = ConfigDict(from_attributes=True)
