from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from . import models, schemas


def create_delivery(
    db: Session, delivery: schemas.DeliveryCreateSchema
) -> models.Delivery:
    """Create a new delivery in the database."""
    db_delivery = models.Delivery(
        id=uuid4(),
        purchase_id=delivery.purchase_id,
        address_id=delivery.address_id,
        user_id=delivery.user_id,
        status=models.DeliverStatus.CREATED,
        # 3 bussines day from now
        delivery_date=datetime.now() + timedelta(days=3),
    )
    db.add(db_delivery)
    db.flush()
    for item in delivery.items:
        db_item = models.DeliveryItem(
            delivery_id=db_delivery.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


def get_delivery(db: Session, delivery_id: UUID) -> Optional[models.Delivery]:
    """
    Get a delivery by its ID.
    Args:
        db (Session): The database session to use for the query.
        delivery_id (UUID): The unique identifier of the
        delivery to retrieve.
    Returns:
        Optional[models.Delivery]: The delivery object if found,
         otherwise None.
    """
    return (
        db.query(models.Delivery)
        .filter(models.Delivery.id == delivery_id)
        .first()
    )


def get_deliveries(
    db: Session, skip: int = 0, limit: int = 10
) -> List[models.Delivery]:
    """Get all deliveries."""
    return (
        db.query(models.Delivery)
        .order_by(models.Delivery.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_delivery(
    db: Session, delivery_id: UUID
) -> Optional[models.Delivery]:
    """Delete a delivery by its ID."""
    db_delivery = get_delivery(db, delivery_id)
    if db_delivery is not None:
        db.delete(db_delivery)
        db.commit()
    return db_delivery
