from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import Sale, SaleDelivery


def get_all_sales(
    db: Session, filters: "ListSalesQueryParamsSchema"  # noqa: F821
) -> List[Sale]:
    """
    Retrieve all sales from the database, ordered by the oldest first.

    Args:
        db (Session): The database session.

    Returns:
        List[Sale]: A list of Sale objects.
    """
    qs = (
        db.query(Sale)
        .options(joinedload(Sale.items))
        .order_by(Sale.created_at.desc())
    )
    if filters.seller_id:
        qs = qs.filter(Sale.seller_id.in_(filters.seller_id))
    if filters.start_date:
        qs = qs.filter(func.date(Sale.created_at) >= filters.start_date)
    if filters.end_date:
        qs = qs.filter(func.date(Sale.created_at) <= filters.end_date)
    if filters.order_number:
        qs = qs.filter(Sale.order_number == filters.order_number)

    return qs.all()


def get_sale_by_id(db: Session, sale_id: UUID) -> Sale:
    """
    Retrieve a sale by its ID.

    Args:
        db (Session): The database session.
        sale_id (UUID): The ID of the sale.

    Returns:
        Sale: The Sale object if found, otherwise None.
    """
    return (
        db.query(Sale)
        .options(joinedload(Sale.items))
        .filter(Sale.id == sale_id)
        .first()
    )


def create_sale(db: Session, sale: Sale) -> Sale:
    """
    Create a new sale in the database.

    Args:
        db (Session): The database session.
        sale (Sale): The Sale object to create.

    Returns:
        Sale: The created Sale object.
    """
    db.add(sale)
    db.flush()
    db.refresh(sale)
    return sale


def create_sale_item(db: Session, sale_item: Sale) -> Sale:
    """
    Create a new sale item in the database.

    Args:
        db (Session): The database session.
        sale_item (Sale): The SaleItem object to create.

    Returns:
        Sale: The created SaleItem object.
    """
    db.add(sale_item)
    db.flush()
    db.refresh(sale_item)
    return sale_item


def get_sale_delivery(
    db: Session, sale_id: UUID, delivery_id: UUID
) -> Optional[SaleDelivery]:
    """
    Retrieve a sale delivery by its ID.

    Args:
        db (Session): The database session.
        sale_id (UUID): The ID of the sale.
        delivery_id (UUID): The ID of the delivery.

    Returns:
        SaleDelivery: The SaleDelivery object if found, otherwise None.
    """
    return (
        db.query(SaleDelivery)
        .filter(SaleDelivery.sale_id == sale_id)
        .filter(SaleDelivery.delivery_id == delivery_id)
        .first()
    )


def associate_delivery_to_sale(
    db: Session, sale_id: UUID, delivery_id: UUID
) -> SaleDelivery:
    """
    Associate a delivery with a sale.
    Args:
        db (Session): The database session.
        sale_id (UUID): The ID of the sale.
        delivery_id (UUID): The ID of the delivery.
    Returns:
        SaleDelivery: The created or existing SaleDelivery object.
    """
    if not get_sale_delivery(db, sale_id, delivery_id):
        sale_delivery = SaleDelivery(sale_id=sale_id, delivery_id=delivery_id)
        db.add(sale_delivery)
        db.commit()
        db.refresh(sale_delivery)
        return sale_delivery
