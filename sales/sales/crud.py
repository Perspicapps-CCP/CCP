from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .models import Sale
from .schemas import ListSalesQueryParamsSchema


def get_all_sales(
    db: Session, filters: ListSalesQueryParamsSchema
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
