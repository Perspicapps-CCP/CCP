import uuid
from typing import List

from sqlalchemy.orm import Session

from . import models


def create_sales_plan(
    db: Session, payload: models.SalesPlan, seller_ids: List[uuid.UUID]
) -> models.SalesPlan:
    """
    Create a new sales plan.
    """
    db.add(payload)
    db.commit()
    for seller_id in seller_ids:
        db.add(
            models.SellerInPlan(
                plan_id=payload.id,
                seller_id=seller_id,
            )
        )
    db.commit()
    db.refresh(payload)
    return payload


def get_all_sales_plans(db: Session) -> List[models.SalesPlan]:
    """
    Get all sales plans.
    """
    return (
        db.query(models.SalesPlan)
        .order_by(models.SalesPlan.created_at.desc())
        .all()
    )


def get_sales_plan(db: Session, plan_id: uuid.UUID) -> models.SalesPlan:
    """
    Get a sales plan by ID.
    """
    return (
        db.query(models.SalesPlan)
        .filter(models.SalesPlan.id == plan_id)
        .first()
    )
