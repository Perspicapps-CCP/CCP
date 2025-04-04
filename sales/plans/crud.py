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
