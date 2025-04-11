from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from . import crud, models


def get_all_sales(db: Session) -> List[models.Sale]:
    """
    Retrieve all sales from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[Sale]: A list of Sale objects.
    """
    return crud.get_all_sales(db)


def get_sale_by_id(db: Session, sale_id: UUID) -> models.Sale:
    """
    Retrieve a sale by its ID.

    Args:
        db (Session): The database session.
        sale_id (UUID): The ID of the sale.

    Returns:
        Sale: The Sale object if found, otherwise None.
    """
    return crud.get_sale_by_id(db, sale_id)
