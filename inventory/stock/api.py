from typing import Annotated, List
import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session
from io import StringIO
from uuid import UUID
from db_dependency import get_db
from rpc_clients.suppliers_client import SuppliersClient

from . import mappers, schemas, services

stock_router = APIRouter(prefix="/stock")


@stock_router.post(
    "",
    response_model=schemas.OperationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def upload_inventory(
    request: schemas.StockRequestSchema,
    db: Session = Depends(get_db),
    suppliers_client: SuppliersClient = Depends(SuppliersClient),
):
    """
    load products stock in a warehouse
    """

    if not services.get_warehouse(db, request.warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The warehouse does not exist",
        )

    product = suppliers_client.get_products([request.product_id])
    if not product or len(product) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The product does not exist",
        )

    successful_records = 0
    failed_records = 0

    try:

        existing_stock = services.get_stock(
            db, request.warehouse_id, request.product_id
        )
        if existing_stock:
            # Actualizar el stock existente
            services.increase_stock(
                db,
                warehouse_id=request.warehouse_id,
                product_id=request.product_id,
                quantity=request.quantity,
            )
        else:
            # Crear un nuevo registro de stock
            services.create_stock(
                db,
                warehouse_id=request.warehouse_id,
                product_id=request.product_id,
                quantity=request.quantity,
            )
        successful_records = 1
    except Exception:
        failed_records = 1

    operation = services.create_operation(
        db,
        file_name="",
        warehouse_id=request.warehouse_id,
        processed_records=successful_records + failed_records,
        successful_records=successful_records,
        failed_records=failed_records,
    )
    return mappers.operation_to_schema(operation)


@stock_router.post(
    "/csv",
    response_model=schemas.OperationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_inventory_csv(
    warehouse_id: Annotated[UUID, Form()],
    inventory_upload: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_db),
    suppliers_client: SuppliersClient = Depends(SuppliersClient),
):
    """
    Carga masiva de inventario desde un archivo CSV.
    El archivo debe contener las columnas: product_id, quantity
    """

    if not services.get_warehouse(db, warehouse_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La bodega no existe",
        )

    if not inventory_upload.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file must be a CSV",
        )

    try:
        contents = await inventory_upload.read()
        s = StringIO(contents.decode("utf-8"))
        df = pd.read_csv(s)

        required_columns = ["product_id", "quantity"]
        if not all(column in df.columns for column in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The CSV file must be contain these columns: {', '.join(required_columns)}",
            )

        inventory_records = df.to_dict("records")
        processed_records = len(inventory_records)
        successful_records = 0
        failed_records = 0

        for record in inventory_records:
            try:
                # Validar que la cantidad sea positiva
                if record["quantity"] < 0:
                    failed_records += 1
                    continue

                # Validar que el producto exista
                product = suppliers_client.get_products([record["product_id"]])
                if not product or len(product) == 0:
                    failed_records += 1
                    continue

                # Buscar si ya existe el producto en la bodega
                existing_stock = services.get_stock(
                    db, warehouse_id, UUID(record["product_id"])
                )

                if existing_stock:
                    # Actualizar el stock existente
                    services.increase_stock(
                        db,
                        warehouse_id=warehouse_id,
                        product_id=UUID(record["product_id"]),
                        quantity=record["quantity"],
                    )
                else:
                    # Crear un nuevo registro de stock
                    services.create_stock(
                        db,
                        warehouse_id=warehouse_id,
                        product_id=UUID(record["product_id"]),
                        quantity=record["quantity"],
                    )

                successful_records += 1
            except Exception:
                failed_records += 1
                continue

        # Registrar la operación
        operation = services.create_operation(
            db,
            file_name=inventory_upload.filename,
            warehouse_id=warehouse_id,
            processed_records=processed_records,
            successful_records=successful_records,
            failed_records=failed_records,
        )

        return mappers.operation_to_schema(operation)

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV file is empty",
        )
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV file is malformed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error when try to process the file: {str(e)}",
        )


@stock_router.get("", response_model=List[schemas.StockResponseSchema])
def list_stock(
    params: schemas.FilterRequest = Depends(), db: Session = Depends(get_db)
):
    """
    Listar el inventario de productos en la bodega.
    """
    stock = services.get_list_stock(
        db, warehouse_id=params.warehouse, product_id=params.product
    )
    return mappers.stock_list_to_schema(stock)
