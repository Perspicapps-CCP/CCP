# Fite to validate the data that is being sent and recieved to the API
import datetime
import uuid
from decimal import Decimal
from typing import Annotated, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

from . import models

NonEmptyStr = Annotated[
    str, StringConstraints(min_length=1, strip_whitespace=True)
]


class DeleteResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class ManufacturerCreateSchema(BaseModel):
    manufacturer_name: str = Field(..., min_length=1)
    identification_type: str = Field(..., min_length=1)
    identification_number: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    contact_phone: str = Field(..., min_length=1)
    email: EmailStr

    @field_validator("identification_type")
    @classmethod
    def validate_identification_type(cls, value):
        try:
            return models.IdentificationType(value)
        except ValueError:
            raise ValueError(
                f"El tipo de identificación '{value}' no es válido."
            )


class ManufacturerProductResponseSchema(BaseModel):
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)


class ErrorDetailResponseSchema(BaseModel):
    row_file: int
    detail: str


class BatchProductResponseSchema(BaseModel):
    total_successful_records: int
    total_errors_records: int
    detail: Optional[List[ErrorDetailResponseSchema]]

    model_config = ConfigDict(from_attributes=True)


class ManufacturerDetailSchema(ManufacturerCreateSchema):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]

    model_config = ConfigDict(from_attributes=True)


class ProductImageSchema(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(BaseModel):
    product_code: NonEmptyStr
    name: NonEmptyStr
    price: Decimal
    images: List[ProductImageSchema]

    @classmethod
    def from_csv_row(cls, row: dict):
        images = []
        if row["images"]:
            images = [
                ProductImageSchema(url=url.strip())
                for url in row["images"].split("|")
            ]
        return cls(
            name=row["name"],
            product_code=row["product_code"],
            price=row["price"],
            images=images,
        )

    @field_validator("price")
    @classmethod
    def check_price_non_negative(cls, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        return value


class ResponseProductDetailSchema(ProductCreateSchema):
    id: uuid.UUID
    images: List[str]
    manufacturer: ManufacturerDetailSchema
    model_config = ConfigDict(from_attributes=True)


class ProductsList(BaseModel):
    productsIds: Optional[List[uuid.UUID]] = None


class ResetResponse(BaseModel):
    msg: str = "Todos los datos fueron eliminados"


class GetProductsSchema(BaseModel):
    product_ids: List[uuid.UUID]


class GetProductsResponseSchema(BaseModel):
    products: List[ResponseProductDetailSchema]

    model_config = ConfigDict(from_attributes=True)


class ImageUploadResponse(BaseModel):
    operation_id: uuid.UUID
    product_id: uuid.UUID
    processed_records: int
    successful_records: int
    failed_records: int
    created_at: datetime.datetime
