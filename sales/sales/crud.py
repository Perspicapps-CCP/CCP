from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from .models import Sale


def get_all_sales(db: Session) -> List[Sale]:
    """
    Retrieve all sales from the database, ordered by the oldest first.

    Args:
        db (Session): The database session.

    Returns:
        List[Sale]: A list of Sale objects.
    """
    return (
        db.query(Sale)
        .options(joinedload(Sale.items))
        .order_by(Sale.created_at.desc())
        .all()
    )


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
