import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from .mappers import sale_to_outbox
from .models import Outbox, OutboxMessageType, OutboxStatus, Sale
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


def get_sale_by_id(db: Session, sale_id: uuid.UUID) -> Sale:
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


def get_pending_sales(db: Session) -> List[Outbox]:
    return (
        db.query(Outbox).filter(
            and_(
                Outbox.status.in_([OutboxStatus.PENDING,OutboxStatus.FAILED]),
                Outbox.message_type == OutboxMessageType.SALES_ORDER,
            )
        )
        .all()
    )


def add_new_sales_to_outbox(db: Session) -> None:
    """
    Implements the outbox pattern for pending sales orders that need to be sent to logistics.

    This function identifies sales orders that have not yet been added to the outbox,
    creates appropriate payload messages, and adds them to the outbox for eventual
    processing by external systems.
    """
    try:
        # Find sales orders that are not in the outbox yet
        new_sales = (
            db.query(Sale)
            .options(joinedload(Sale.items))
            .outerjoin(
                Outbox,
                and_(
                    Outbox.message_type == OutboxMessageType.SALES_ORDER,
                    Outbox.payload.isnot(None),
                    Sale.id == Outbox.id,
                ),
            )
            .filter(Outbox.id == None)
            .all()
        )

        if not new_sales:
            return
    
        # Add new sales to outbox
        for sale in new_sales:
            outbox_item = sale_to_outbox(sale)
            db.add(outbox_item)

        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to process pending sales: {str(e)}") from e


def set_status_outbox_item(
    db: Session, outbox_id:uuid.UUID, outbox_status: OutboxStatus, message: Optional[str]=None
) -> bool:
    """
    Mark an outbox item as sent once it's been successfully processed.

    Args:
        db (Session): The database session.
        outbox_id: The ID of the outbox item.
        outbox_status (OutboxStatus): The new status to set.
        message (Optional[str], optional): Optional error message. Defaults to None.
    """
    outbox_item = db.query(Outbox).filter(Outbox.id == outbox_id).first()
    if outbox_item:
        outbox_item.status = outbox_status
        outbox_item.error_message = message
        outbox_item.processed_at = datetime.now()
        outbox_item.attempt_count += 1
        db.commit()
        return True
    return False
