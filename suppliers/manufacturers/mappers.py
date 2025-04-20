from . import models, schemas


def manufacturer_to_schema(
    manufacturer: models.Manufacturer,
) -> schemas.ManufacturerDetailSchema:
    return schemas.ManufacturerDetailSchema(
        id=manufacturer.id,
        manufacturer_name=manufacturer.name,
        identification_type=manufacturer.identification_type,
        identification_number=manufacturer.identification_number,
        address=manufacturer.address,
        contact_phone=manufacturer.contact_phone,
        email=manufacturer.email,
        created_at=manufacturer.created_at,
        updated_at=manufacturer.updated_at,
    )


def product_to_schema(
    product: models.ManufacturerProduct,
) -> schemas.ResponseProductDetailSchema:
    return schemas.ResponseProductDetailSchema(
        id=product.id,
        product_code=product.code,
        name=product.name,
        price=product.price,
        images=[image.url for image in product.images],
        manufacturer=manufacturer_to_schema(product.manufacturer),
    )


def operation_to_schema(
    operation: models.ProductImage,
) -> schemas.ImageUploadResponse:
    return schemas.ImageUploadResponse(
        operation_id=operation.id,
        product_id=operation.product_id,
        processed_records=operation.processed_records,
        successful_records=operation.successful_records,
        failed_records=operation.failed_records,
        created_at=operation.created_at,
    )
