from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
    db: Session = Depends(get_db),
) -> List[schemas.SaleDetailSchema]:
    """
    List all sales.
    """
    sales = services.get_all_sales(db)
    return mappers.sales_to_schema(sales)


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
