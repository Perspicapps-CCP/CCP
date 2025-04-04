import uuid
from typing import List

from sqlalchemy.orm import Session

from . import crud, models, schemas


def create_sales_plan(
    db: Session,
    payload: schemas.CreateSalesPlanSchema,
) -> schemas.SalesPlanDetailSchema:
    """
    Create a new sales plan.
    """
    db_plan = crud.create_sales_plan(
        db,
        models.SalesPlan(
            product_id=payload.product_id,
            goal=payload.goal,
            start_date=payload.start_date,
            end_date=payload.end_date,
        ),
        payload.seller_ids,
    )
    return db_plan


def get_all_sales_plans(
    db: Session,
) -> List[models.SalesPlan]:
    """
    List all sales plans.
    """
    db_plans = crud.get_all_sales_plans(db)
    return db_plans


def get_sales_plan(
    db: Session,
    plan_id: uuid.UUID,
) -> models.SalesPlan:
    """
    Get a sales plan by ID.
    """
    db_plan = crud.get_sales_plan(db, plan_id)
    return db_plan
