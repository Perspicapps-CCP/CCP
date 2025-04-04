import uuid
from typing import Dict, List

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


@plans_router.get(
    "/",
    response_model=List[schemas.SalesPlanDetailSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "List of all sales plans.",
        }
    },
)
def list_plans(
    db: Session = Depends(get_db),
) -> List[schemas.SalesPlanDetailSchema]:
    """
    List all sales plans.
    """
    plans = services.get_all_sales_plans(db)
    return mappers.plans_to_schema(plans)


@plans_router.get(
    "/{plan_id}",
    response_model=schemas.SalesPlanDetailSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.ErrorResponseSchema,
            "description": "Sales plan not found",
        }
    },
)
def get_plan(
    plan_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> schemas.SalesPlanDetailSchema:
    """
    Get a sales plan by ID.
    """
    plan = services.get_sales_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales plan not found",
        )
    return mappers.plan_to_schema(plan)
