from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from rpc_clients.schemas import (
    AddressSchema,
    DeliverySchema,
    ProductSchema,
    UserAuthSchema,
    UserSchema,
)
from sales import crud as sales_crud
from sellers import crud as sellers_crud


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
    seller: Optional[UserSchema]
    client: UserSchema
    order_number: int
    address: Optional[AddressSchema]
    total_value: Decimal
    currency: str
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[SaleItemSchema]
    deliveries: List[Optional[DeliverySchema]]

    model_config = ConfigDict(from_attributes=True)


class ListSalesQueryParamsSchema(BaseModel):
    order_number: Optional[int] = None
    seller_name: Optional[str] = None
    seller_id: Optional[List[UUID]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class CreateSaleItemSchema(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)

    model_config = ConfigDict(from_attributes=True)


class CreateSaleSchema(BaseModel):
    items: List[CreateSaleItemSchema]
    client_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("client_id")
    @classmethod
    def validate_product_id(
        cls, client_id: Optional[UUID], info: ValidationInfo
    ) -> UUID:
        context = info.context
        user: UserAuthSchema = context.get("user")
        db = context.get("db")
        if user.is_seller:
            if not client_id:
                raise ValueError("Client ID is required for sellers.")

            if not sellers_crud.does_client_for_seller_exist(
                db, user.id, client_id
            ):
                raise ValueError("Client is not associated with this seller.")
            return client_id
        elif user.is_client:
            return user.id
        else:
            raise ValueError(
                "Invalid user type. Only sellers and clients are allowed."
            )

    @model_validator(mode="after")
    def validate_client_id_for_sellers(
        self,
        info: ValidationInfo,
    ):
        """
        Validates the client ID for sellers.
        Args:
            values (CreateSaleSchema): The sale values to validate.
            info (ValidationInfo): The validation information.
        Returns:
            CreateSaleSchema: The validated sale values.
        Raises:
            ValueError: If the client ID is invalid or
            not associated with the seller.
        """
        context = info.context
        user: UserAuthSchema = context.get("user")
        if user.is_seller and not self.client_id:
            raise ValueError("Client ID is required for sellers.")
        return self


class CreateSaleDeliverySchema(BaseModel):
    """
    Schema for creating a sale delivery.
    """

    sale_id: UUID
    delivery_id: UUID

    model_config = ConfigDict(from_attributes=True)

    @field_validator("sale_id")
    @classmethod
    def validate_sale_id(cls, sale_id: UUID, info: ValidationInfo) -> UUID:
        """
        Validates the delivery ID.
        Args:
            sale_id (UUID): The sale ID to validate.
            info (ValidationInfo): The validation information.
        Returns:
            UUID: The validated sale_id ID.
        Raises:
            ValueError: If the sale_id ID is invalid or
            not associated with the sale.
        """
        context = info.context
        db = context.get("db")
        sale = sales_crud.get_sale_by_id(db, sale_id)
        if not sale:
            raise ValueError("Sale not found.")
        return sale_id
