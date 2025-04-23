from datetime import datetime
from typing import List, Generator, Any
from uuid import UUID
from sqlalchemy import and_, update
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from deliveries import models, schemas


def get_deliveries(db: Session) -> Generator[models.Delivery, Any, None]:
    query = (
        db.query(models.Delivery)
        .options(joinedload(models.Delivery.driver))
        .join(models.Driver, models.Driver.id == models.Delivery.driver_id)
        .yield_per(100)
    ) 
    for delivery in query:
        yield delivery


def get_delivery_items(db: Session, delivery_id: UUID) -> Generator[models.DeliveryItem, Any, None]:
    query = (
        db.query(models.DeliveryItem)
        .filter(models.DeliveryItem.delivery_id == delivery_id)
        .yield_per(100)
    )
    for delivery_item in query:
        yield delivery_item


def get_orders_pending_to_delivery(db: Session) -> dict:
    list_sales_by_warehouse = (
        db.query(models.DeliveryItem.sales_id, models.DeliveryItem.warehouse_id)
        .distinct()
        .filter(models.DeliveryItem.delivery_id == None)
        .all()
    )

    warehouse_orders = {}
    for item in list_sales_by_warehouse:
        if item.warehouse_id not in warehouse_orders:
            warehouse_orders[item.warehouse_id] = []
        warehouse_orders[item.warehouse_id].append(item.sales_id)

    return warehouse_orders


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
    return (db.query(models.Driver)
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


def create_delivery_items(
    db: Session, sale: schemas.PayloadSaleSchema
) -> bool:
    """
    Create delivery items in the database based on the provided sale schema.
    This function iterates through the sales items in the sale schema,
    creates a new delivery item instance for each item, and adds it to the database session.
    If an IntegrityError occurs, it rolls back the session.

    Args:
        db (Session): The database session.
        sale (schemas.PayloadSaleSchema): The sale schema object containing sales items.

    Returns:
        bool: True if delivery items were created successfully, False otherwise.
    """
    try:
        for item in sale.sales_items:
            db_item = models.DeliveryItem(
                sales_id=sale.sales_id,
                order_number=sale.order_number,
                product_id=item.product_id,
                warehouse_id=item.warehouse_id,
                address_id=sale.address_id,
            )
            db.add(db_item)
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


def create_order_delivery(db: Session, warehouse_id: UUID) -> models.Delivery:
    db_delivery = models.Delivery(
        warehouse_id=warehouse_id,
    )
    db.add(db_delivery)
    db.flush()
    db.refresh(db_delivery)
    return db_delivery


def update_delivery_items(
    db: Session,
    delivery_id: UUID,
    sales_orders: List[UUID],
    warehouse_id: UUID,
) -> int:
    update_query = (
        update(models.DeliveryItem)
        .values(
            delivery_id=delivery_id,
        )
        .where(
            and_(
                models.DeliveryItem.sales_id.in_(sales_orders),
                models.DeliveryItem.warehouse_id == warehouse_id,
                models.DeliveryItem.delivery_id == None,
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
        pending_delivery_orders = get_orders_pending_to_delivery(db)

        if not pending_delivery_orders:
            return None

        created_deliveries = []
        # For each warehouse, create deliveries with max 10 orders each
        for warehouse_id, sale_orders in pending_delivery_orders.items():
            order_chunks = [
                sale_orders[i : i + 10] for i in range(0, len(sale_orders), 10)
            ]

            # Create a delivery for each chunk
            for chunk in order_chunks:
                db_delivery = create_order_delivery(db, warehouse_id)
                created_deliveries.append(
                    {
                        "delivery": db_delivery,
                        "sale_orders": chunk,
                        "warehouse_id": warehouse_id,
                    }
                )

        for delivery_data in created_deliveries:
            delivery = delivery_data["delivery"]
            sale_orders = delivery_data["sale_orders"]
            warehouse_id = delivery_data["warehouse_id"]

            result = update_delivery_items(
                db, delivery.id, sale_orders, warehouse_id
            )
            if result == 0:
                db.rollback()
                return None

        db.commit()
        return [
            delivery_data["delivery"] for delivery_data in created_deliveries
        ]

    except Exception as e:
        db.rollback()
        print(f"Error creating deliveries: {e}")
        return None

