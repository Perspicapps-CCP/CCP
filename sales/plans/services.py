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
