import csv
import datetime
from io import StringIO
from typing import Annotated, Dict, List
from uuid import UUID

from common.api import get_auth_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import exceptions, mappers, schemas, services

sales_router = APIRouter(prefix="/sales", tags=["Sales"])


@sales_router.get(
    "/",
    response_model=List[schemas.SaleDetailSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "List of all sales.",
        }
    },
)
def list_sales(
    filter_query: Annotated[schemas.ListSalesQueryParamsSchema, Query()],
    db: Session = Depends(get_db),
) -> List[schemas.SaleDetailSchema]:
    """
    List all sales.
    """
    sales = services.get_all_sales(db, filter_query)
    response = mappers.sales_to_schema(sales)
    if filter_query.seller_name:
        response = [
            sale
            for sale in response
            if filter_query.seller_name.lower()
            in sale.seller.full_name.lower()
        ]
    return response


@sales_router.post(
    "/",
    response_model=schemas.SaleDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Sale created successfully.",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid input data.",
        },
    },
)
def create_sale(
    payload: Dict,
    db: Session = Depends(get_db),
    user=Depends(get_auth_user),
) -> schemas.SaleDetailSchema:
    """
    Create a new sale.
    """
    try:
        payload = schemas.CreateSaleSchema.model_validate(
            payload, context={"user": user, "db": db}
        )
        sale = services.create_sale(db, user, payload)
        return mappers.sale_to_schema(sale)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )
    except exceptions.SaleCantBeCreated as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Timeout error, please try again in a few minutes.",
        )


@sales_router.get(
    "/export",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Export all sales as a CSV file.",
        }
    },
)
def export_sales_as_csv(
    filter_query: Annotated[schemas.ListSalesQueryParamsSchema, Query()],
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export all sales as a CSV file.
    """
    # Retrieve all sales from the database
    sales_objects = services.get_all_sales(db, filter_query)
    sales = mappers.sales_to_schema(sales_objects)

    # Create a CSV writer
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Sale ID",
            "Order Number",
            "Seller ID",
            "Seller Name",
            "Total Value",
            "Currency",
            "Sale At",
        ]
    )

    # Write sales data to the CSV
    for sale in sales:
        writer.writerow(
            [
                str(sale.id),
                sale.order_number,
                str(sale.seller.id),
                sale.seller.full_name,
                sale.total_value,
                sale.currency,
                sale.created_at.isoformat(),
            ]
        )

    # Reset the pointer of the StringIO object
    output.seek(0)

    # Return the CSV as a streaming response
    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    seller = (
        [
            sale.seller
            for sale in sales
            if sale.seller.id == filter_query.seller_id[0]
        ]
        if filter_query.seller_id
        else []
    )
    for_seller = f"_{seller[0].full_name}" if seller else ""
    file_name = f"{date_now}{for_seller}_sales.csv"
    # Clean file name
    file_name = file_name.replace(" ", "_").lower()
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


@sales_router.get(
    "/{sale_id}",
    response_model=schemas.SaleDetailSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Sale not found.",
        }
    },
)
def get_sale(
    sale_id: UUID, db: Session = Depends(get_db)
) -> schemas.SaleDetailSchema:
    """
    Retrieve a specific sale by ID.
    """
    sale = services.get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found.",
        )
    return mappers.sale_to_schema(sale)
