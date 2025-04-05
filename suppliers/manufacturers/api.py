import csv
import io
from typing import Annotated, List, Optional
from uuid import UUID
import uuid
from google.cloud import storage
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from db_dependency import get_db
from storage_dependency import get_storage_bucket
from . import mappers, schemas, services

manufacturers_router = APIRouter(prefix="/manufacturers")


@manufacturers_router.post(
    "/", response_model=schemas.ManufacturerDetailSchema
)
def create_manufacturer(
    manufacturer: schemas.ManufacturerCreateSchema,
    db: Session = Depends(get_db),
):
    if services.get_manufacturer_by_id_type(db=db, manufacturer=manufacturer):
        raise HTTPException(
            status_code=409, detail="Manufacturer already exists"
        )
    manufacturer = services.create_manufacturer(
        db=db, manufacturer=manufacturer
    )
    return mappers.manufacturer_to_schema(manufacturer)


@manufacturers_router.get(
    "/{manufacturer_id}", response_model=schemas.ManufacturerDetailSchema
)
def manufacturer_detail(manufacturer_id: UUID, db: Session = Depends(get_db)):
    db_manufacturer = services.get_manufacturer(
        db, manufacturer_id=manufacturer_id
    )
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return mappers.manufacturer_to_schema(db_manufacturer)


@manufacturers_router.get(
    "/", response_model=List[schemas.ManufacturerDetailSchema]
)
def list_all_manufacturers(db: Session = Depends(get_db)):
    manufacturers = services.get_manufacturers(db)
    return [
        mappers.manufacturer_to_schema(manufacturer)
        for manufacturer in manufacturers
    ]


@manufacturers_router.post(
    "/{manufacturer_id}/products/batch/",
    response_model=schemas.BatchProductResponseSchema,
)
async def create_batch_products(
    manufacturer_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    db_manufacturer = services.get_manufacturer(
        db, manufacturer_id=manufacturer_id
    )
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    contents = await file.read()
    decoded_contents = contents.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(decoded_contents))
    products = process_file(csv_reader)
    return services.create_bulk_products(
        manufacturer_id=manufacturer_id, db=db, products=products
    )


def process_file(csv_reader):
    validated_products = []
    headers = csv_reader.fieldnames
    validated_products = []
    validation_errors = []
    EXPECTED_HEADERS = ["name", "product_code", "price", "images"]
    if not headers or set(headers) != set(EXPECTED_HEADERS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid headers. Expected headers: {EXPECTED_HEADERS}, but got: {headers}",
        )

    for line_number, row in enumerate(csv_reader, start=2):
        try:
            validated_product = schemas.ProductCreateSchema.from_csv_row(row)
            validated_products.append(validated_product)
        except ValidationError as e:
            validation_errors.append(
                {
                    "line": line_number,
                    "errors": e.errors(),
                }
            )
    if validation_errors:
        formatted_errors = [
            {
                "line": error["line"],
                "location": str(error["errors"][0].get("loc", "")),
                "message": str(error["errors"][0].get("msg", "")),
            }
            for error in validation_errors
        ]

        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation failed for some products",
                "validation_errors": formatted_errors,
            },
        )
    return validated_products


@manufacturers_router.post(
    "/listProducts", response_model=List[schemas.ResponseProductDetailSchema]
)
def list_products_by_ids(
    productsIds: Optional[schemas.ProductsList] = None,
    db: Session = Depends(get_db),
):
    products = services.get_products(db, productsIds=productsIds.productsIds)
    return [mappers.product_to_schema(product) for product in products]


@manufacturers_router.get(
    "/{manufacturer_id}/products",
    response_model=List[schemas.ResponseProductDetailSchema],
)
def list_manufacturer_products(
    manufacturer_id: UUID, db: Session = Depends(get_db)
):
    products = services.get_products(db, manufacturer_id=manufacturer_id)
    return [mappers.product_to_schema(product) for product in products]


@manufacturers_router.post("/reset", response_model=schemas.ResetResponse)
def reset(db: Session = Depends(get_db)):
    services.reset(db)
    return schemas.ResetResponse


@manufacturers_router.post(
    "/{manufacturer_id}/products/image",
    response_model=schemas.ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@manufacturers_router.post(
    "/{manufacturer_id}/products/image/",
    response_model=schemas.ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_images(
    manufacturer_id: UUID,
    product_id: Annotated[UUID, Form()],
    product_image: Annotated[List[UploadFile], File(...)],
    db: Session = Depends(get_db),
    bucket: storage.Bucket = Depends(get_storage_bucket),
):
    db_manufacturer = services.get_manufacturer(
        db, manufacturer_id=manufacturer_id
    )
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    product = services.get_product(
        db, manufacturer_id=manufacturer_id, product_id=product_id
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    processed_records = len(product_image)
    successful_records = 0
    failed_records = 0

    try:

        for image in product_image:
            try:
                content_type = image.content_type
                if not content_type or not content_type.startswith("image/"):
                    failed_records += 1
                    continue

                if await services.file_is_too_large(image):
                    failed_records += 1
                    continue

                filename = f"{uuid.uuid4()}_{image.filename}"
                blob = bucket.blob(f"products/{product_id}/{filename}")
                blob.upload_from_file(image.file)

                services.save_image_product_uri(
                    db=db,
                    product_id=product_id,
                    image_name=filename,
                )

                successful_records += 1
            except Exception:
                failed_records += 1

        operation = services.create_operation(
            db=db,
            product_id=product_id,
            processed_records=processed_records,
            successful_records=successful_records,
            failed_records=failed_records,
        )

        return mappers.operation_to_schema(operation)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error when try to process the file: {str(e)}",
        )
