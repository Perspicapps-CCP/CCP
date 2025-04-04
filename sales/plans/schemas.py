# Schema for plans data validation
import uuid
from datetime import date, datetime
from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)

from rpc_clients.schemas import ProductSchema, SellerSchema
from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient


class ErrorResponseSchema(BaseModel):
    detail: str


class SalesPlanBaseSchema(BaseModel):
    goal: int = Field(ge=1)
    start_date: date
    end_date: date
    model_config = ConfigDict(from_attributes=True)


class CreateSalesPlanSchema(SalesPlanBaseSchema):
    seller_ids: List[uuid.UUID]
    product_id: uuid.UUID

    @field_validator("product_id")
    def validate_product_id(cls, product_id: uuid.UUID) -> uuid.UUID:
        products_client = SuppliersClient()
        products = products_client.get_products([product_id])
        if len(products) == 0:
            raise ValueError("Product ID is invalid.")
        return product_id

    @field_validator("end_date")
    def validate_dates(
        cls, end_date: datetime, info: ValidationInfo
    ) -> datetime:
        if start_date := info.data.get("start_date"):
            if end_date < start_date:
                raise ValueError("End date must be after start date.")
        return end_date

    @field_validator("seller_ids")
    def validate_seller_ids(
        cls, seller_ids: list[uuid.UUID]
    ) -> List[uuid.UUID]:
        if len(seller_ids) == 0:
            raise ValueError("At least one seller ID must be provided.")

        users_client = UsersClient()
        sellers = users_client.get_sellers(seller_ids)
        if len(sellers) != len(seller_ids):
            raise ValueError("Some seller IDs are invalid.")
        return seller_ids


class SalesPlanDetailSchema(SalesPlanBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    sellers: List[SellerSchema]
    product: ProductSchema | None
