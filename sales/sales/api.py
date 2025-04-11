from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import mappers, schemas, services

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
