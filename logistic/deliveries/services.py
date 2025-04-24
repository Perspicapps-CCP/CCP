from datetime import datetime
from typing import Dict, List, Generator
from uuid import UUID
from sqlalchemy import Tuple, and_, update
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from deliveries import models, schemas


def get_deliveries(db: Session) -> Generator[models.Delivery, None, None]:
    query = (
        db.query(models.Delivery)
        .options(joinedload(models.Delivery.driver))
        .join(models.Driver, models.Driver.id == models.Delivery.driver_id)
        .yield_per(100)
    )
    for delivery in query:
        yield delivery


def get_delivery_items(
    db: Session, delivery_id: UUID
) -> Generator[Tuple, None, None]:
    query = (
        db.query(
            models.DeliveryItem,
            models.DeliveryAddress.address.label('delivery_address'),
        )
        .join(
            models.DeliveryStop,
            models.DeliveryStop.id == models.DeliveryItem.delivery_stop_id,
        )
        .join(
            models.DeliveryAddress,
            models.DeliveryAddress.address_id
            == models.DeliveryStop.address_id,
        )
        .filter(models.DeliveryStop.delivery_id == delivery_id)
        .yield_per(100)
    )
    for delivery_item in query:
        yield delivery_item


def get_stops_pending_to_delivery(db: Session) -> List[Tuple]:
    query = (
        db.query(
            models.DeliveryStop.id,
            models.DeliveryItem.sales_id,
            models.DeliveryItem.warehouse_id,
        )
        .join(
            models.DeliveryItem,
            models.DeliveryItem.delivery_stop_id == models.DeliveryStop.id,
        )
        .distinct()
        .filter(models.DeliveryStop.delivery_id.is_(None))
    )
    return query.all()


def get_driver_available(
    db: Session, delivery_date: datetime
) -> models.Driver:
    """
    Get the first available driver in specific day from the database.
    This function queries the database for drivers who are not currently assigned to any deliveries
    on the specified delivery date.

    Args:
        db (Session): The database session.

    Returns:
        List[models.Driver]: List of available driver objects.
    """
    return (
        db.query(models.Driver)
        .outerjoin(
            models.Delivery,
            and_(
                models.Delivery.driver_id == models.Driver.id,
                models.Delivery.delivery_date == delivery_date,
            ),
        )
        .filter(models.Delivery.id == None)
        .first()
    )


def create_driver(
    db: Session, driver: schemas.DriverCreateSchema
) -> models.Driver:
    """
    Create a new driver in the database.
    This function takes a driver schema object, creates a new driver instance,
    and adds it to the database session. It then commits the session and refreshes

    Args:
        db (Session): The database session.
        driver (schemas.DriverCreateSchema): The driver schema object containing driver details.

    Returns:
        models.Driver: The created driver object.
    """
    db_driver = models.Driver(
        name=driver.driver_name,
        license_plate=driver.license_plate,
        phone_number=driver.phone_number,
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def add_delivery_stop(
    db: Session, sales_id: UUID, order_number: int, address_id: UUID
) -> models.DeliveryStop:
    db_delivery_stop = models.DeliveryStop(
        sales_id=sales_id,
        order_number=order_number,
        address_id=address_id,
    )
    db.add(db_delivery_stop)
    db.flush()
    db.refresh(db_delivery_stop)
    return db_delivery_stop


def add_delivery_address(
    db: Session, address_id: UUID, address: str
) -> models.DeliveryAddress:
    db_delivery_address = models.DeliveryAddress(
        address_id=address_id,
        address=address,
    )
    db.add(db_delivery_address)
    db.flush()
    db.refresh(db_delivery_address)
    return db_delivery_address


def add_delivery_item(
    db: Session,
    sales_id: UUID,
    order_number: int,
    product_id: UUID,
    warehouse_id: UUID,
    delivery_stop_id: UUID,
) -> models.DeliveryItem:
    db_delivery_item = models.DeliveryItem(
        sales_id=sales_id,
        order_number=order_number,
        product_id=product_id,
        warehouse_id=warehouse_id,
        delivery_stop_id=delivery_stop_id,
    )
    db.add(db_delivery_item)
    db.flush()
    db.refresh(db_delivery_item)
    return db_delivery_item


def group_items_by_warehouse(
    sale: schemas.PayloadSaleSchema,
) -> Dict[UUID, List[schemas.PayloadSaleItemSchema]]:
    items_by_warehouse = {}
    for item in sale.sales_items:
        if item.warehouse_id not in items_by_warehouse:
            items_by_warehouse[item.warehouse_id] = []
        items_by_warehouse[item.warehouse_id].append(item)
    return items_by_warehouse


def group_stops_by_warehouse(pending_delivery_stops) -> Dict[UUID, List[UUID]]:
    stops_by_warehouse = {}
    for stop_id, _, warehouse_id in pending_delivery_stops:
        if warehouse_id not in stops_by_warehouse:
            stops_by_warehouse[warehouse_id] = []
        stops_by_warehouse[warehouse_id].append(stop_id)
    return stops_by_warehouse


def create_order_delivery(db: Session, warehouse_id: UUID) -> models.Delivery:
    db_delivery = models.Delivery(
        warehouse_id=warehouse_id,
    )
    db.add(db_delivery)
    db.flush()
    db.refresh(db_delivery)
    return db_delivery


def update_delivery_stops(
    db: Session, delivery_id: UUID, delivery_stops: List[UUID]
) -> int:
    update_query = (
        update(models.DeliveryStop)
        .values(
            delivery_id=delivery_id,
        )
        .where(
            and_(
                models.DeliveryStop.id.in_(delivery_stops),
                models.DeliveryStop.delivery_id == None,
            )
        )
    )

    result = db.execute(update_query)
    return result.rowcount


def update_driver_on_delivery(
    db: Session, delivery_id: UUID, driver_id: UUID, delivery_date: datetime
) -> bool:
    """
    Update the driver assigned to a delivery in the database.
    This function takes a delivery ID and a driver ID,
    and updates the delivery record with the new driver ID.
    """
    try:
        update_query = (
            update(models.Delivery)
            .values(
                driver_id=driver_id,
                delivery_date=delivery_date,
                status=models.DeliverStatus.SCHEDULED,
            )
            .where(
                models.Delivery.id == delivery_id,
            )
        )

        result = db.execute(update_query)
        if result.rowcount == 0:
            db.rollback()
            return False

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating driver on delivery: {e}")
        return False


def create_delivery_stops_transaction(
    db: Session, sale: schemas.PayloadSaleSchema
) -> bool:
    """
    Create a delivery transaction in the database.
    This function takes a sale schema object, creates delivery stops and items,
    and adds them to the database session. It then commits the session.
    If any integrity error occurs, it rolls back the session and returns False.

    Args:
        db (Session): The database session.
        sale (schemas.PayloadSaleSchema): The sale schema object containing sales items.

    Returns:
        bool: True if delivery items were created successfully, False otherwise.
    """
    try:

        items_by_warehouse = group_items_by_warehouse(sale)

        db_delivery_address = add_delivery_address(
            db,
            address_id=sale.address_id,
            address=sale.address,
        )

        for warehouse_id, warehouse_items in items_by_warehouse.items():
            db_delivery_stop = add_delivery_stop(
                db,
                sales_id=sale.sales_id,
                order_number=sale.order_number,
                address_id=db_delivery_address.address_id,
            )

            for item in warehouse_items:
                add_delivery_item(
                    db,
                    sales_id=sale.sales_id,
                    order_number=sale.order_number,
                    product_id=item.product_id,
                    warehouse_id=item.warehouse_id,
                    delivery_stop_id=db_delivery_stop.id,
                )
            db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            print(f"Duplicate entry found: {e.orig.diag.message_detail}")
            return True
        else:
            print(f"Integrity error: {e.orig}")
            return False
    except Exception as e:
        db.rollback()
        print(f"Error creating delivery items: {e}")
        return False


def create_delivery_transaction(db: Session) -> List[models.Delivery]:
    """
    Create delivery transactions based on sales orders pending to delivery.
    This function retrieves pending delivery orders from the database,
    creates deliveries for each warehouse, and updates the delivery items.
    It commits the changes to the database and returns a list of created deliveries.

    Args:
        db (Session): The database session.

    Returns:
        List[models.Delivery]: List of created delivery objects or None if no pending items.
    """
    try:
        pending_delivery_stops = get_stops_pending_to_delivery(db)

        if not pending_delivery_stops:
            return None

        stops_by_warehouse = group_stops_by_warehouse(pending_delivery_stops)

        created_deliveries = []
        for warehouse_id, stop_ids in stops_by_warehouse.items():
            # Divide stops into chunks of 10
            stop_chunks = [
                stop_ids[i : i + 10] for i in range(0, len(stop_ids), 10)
            ]

            # Create a delivery for each chunk
            for chunk in stop_chunks:
                db_delivery = create_order_delivery(db, warehouse_id)

                result = update_delivery_stops(
                    db,
                    db_delivery.id,
                    chunk,
                )
                if result == 0:
                    db.rollback()
                    return None

                created_deliveries.append(db_delivery)

        db.commit()
        return created_deliveries
    except Exception as e:
        db.rollback()
        print(f"Error creating deliveries: {e}")
        return None
