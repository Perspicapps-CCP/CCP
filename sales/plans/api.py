from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import mappers, schemas, services

plans_router = APIRouter(prefix="/plans")


@plans_router.post(
    "/",
    response_model=schemas.SalesPlanDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": schemas.ErrorResponseSchema,
            "description": "Bad Request",
        }
    },
)
def create_plan(
    payload: Dict,
    db: Session = Depends(get_db),
) -> schemas.SalesPlanDetailSchema:
    """
    Create a new sales plan.
    """
    try:
        payload = schemas.CreateSalesPlanSchema.model_validate(payload)
        plans = services.create_sales_plan(db, payload)
        return mappers.plan_to_schema(plans)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Timeout error, please try again in a few minutes.",
        )
