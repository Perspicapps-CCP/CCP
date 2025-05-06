from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from . import crud, models, schemas


def get_all_sales(
    db: Session, filters: schemas.ListSalesQueryParamsSchema
) -> List[models.Sale]:
    """
    Retrieve all sales from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[Sale]: A list of Sale objects.
    """
    return crud.get_all_sales(db, filters)


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


def get_pending_sales(db: Session) -> List[models.Outbox]:
    """
    Retrieve all pending sales from the Outbox table.

    Args:
        db (Session): The database session.

    Returns:
        List[Outbox]: A list of Outbox objects with pending sales.
    """
    return crud.get_pending_sales(db)


def add_new_sales_to_outbox(db: Session) -> None:
    """
    Process pending sales and send them to the logistics service.

    Args:
        db (Session): The database session.

    Returns:
        None
    """
    crud.add_new_sales_to_outbox(db)


def set_status_outbox_item(
    db: Session, outbox_id: UUID, outbox_status: models.OutboxStatus, message: Optional[str]=None
) -> bool:
    """
    Set the status of an outbox item.

    Args:
        db (Session): The database session.
        outbox_id (UUID): The ID of the outbox item.
        outbox_status (OutboxStatus): The new status to set.
        message (Optional[str]): Optional message to set in the outbox item.
    
    Returns:
        bool: True if the status was updated successfully, False otherwise.
    """
    return crud.set_status_outbox_item(db, outbox_id, outbox_status, message)
