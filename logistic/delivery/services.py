from datetime import datetime
import re
from typing import Dict, List, Generator, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from delivery import models, schemas
from .unit_of_work import unit_of_work
from .helpers import group_items_by_warehouse, group_stops_by_warehouse


# Read-only services (no transactions needed)
def get_deliveries(db: Session) -> Generator[models.Delivery, None, None]:
    """Get all deliveries with their associated drivers."""
    with unit_of_work(db) as uow:
        for delivery in uow.delivery.get_all():
            yield delivery


def get_delivery_items(
    db: Session, delivery_id: UUID
) -> Generator[Tuple, None, None]:
    """Get all items for a specific delivery."""
    with unit_of_work(db) as uow:
        for delivery_item in uow.delivery_item.get_by_delivery_id(delivery_id):
            yield delivery_item


def get_delivery(db: Session, delivery_id: UUID) -> Optional[models.Delivery]:
    """Get a specific delivery by ID."""
    with unit_of_work(db) as uow:
        return uow.delivery.get_by_id(delivery_id)


def get_stops_pending_to_delivery(
    db: Session, warehouse_id: UUID
) -> List[Tuple]:
    """Get stops pending assignment to deliveries."""
    with unit_of_work(db) as uow:
        return uow.delivery_stop.get_pending_stops(warehouse_id)


def get_driver_available(
    db: Session, delivery_date: datetime
) -> Optional[models.Driver]:
    """Get the first available driver on a specific date."""
    with unit_of_work(db) as uow:
        return uow.driver.get_available(delivery_date)


def get_deliveries_without_stops_ordered(db: Session) -> List[models.Delivery]:
    """Get deliveries without ordered stops."""
    with unit_of_work(db) as uow:
        return uow.delivery.get_without_stops_ordered()


def get_delivery_route(
    db: Session, delivery_id: UUID
) -> List[Tuple[models.Delivery, models.DeliveryStop, models.DeliveryAddress]]:
    """Get the route for a specific delivery."""
    with unit_of_work(db) as uow:
        return uow.delivery.get_route(delivery_id)


def get_delivery_address_without_geocoding(
    db: Session,
) -> List[models.DeliveryAddress]:
    """Get addresses without geocoding information."""
    with unit_of_work(db) as uow:
        return uow.delivery_address.get_without_geocoding()


# Write services (transactions needed)
def create_driver(
    db: Session, driver: schemas.DriverCreateSchema
) -> models.Driver:
    """Create a new driver in the database."""
    with unit_of_work(db) as uow:
        db_driver = uow.driver.create(driver)
        uow.commit()
        return db_driver


def update_driver_on_delivery(
    db: Session, delivery_id: UUID, driver_id: UUID, delivery_date: datetime
) -> bool:
    """Update the driver assigned to a delivery."""
    with unit_of_work(db) as uow:
        success = uow.delivery.update_driver(
            delivery_id, driver_id, delivery_date
        )
        if not success:
            return False
        uow.commit()
        return True


def update_order_delivery_stops(db: Session, list_stop_id: List[Dict]) -> bool:
    """Update the order of delivery stops."""
    with unit_of_work(db) as uow:
        success = uow.delivery_stop.update_stop_order(list_stop_id)
        if not success:
            return False
        uow.commit()
        return True


def create_delivery_stops_transaction(
    db: Session, sale: schemas.PayloadSaleSchema
) -> bool:
    """Create delivery stops and items for a sale."""
    with unit_of_work(db) as uow:
        try:
            items_by_warehouse = group_items_by_warehouse(sale)
            db_delivery_address = uow.delivery_address.create(sale.address)

            for warehouse_id, warehouse_items in items_by_warehouse.items():
                db_delivery_stop = uow.delivery_stop.create(
                    sales_id=sale.sales_id,
                    order_number=sale.order_number,
                    address_id=db_delivery_address.id,
                )

                for item in warehouse_items:
                    uow.delivery_item.create(
                        sales_id=sale.sales_id,
                        order_number=sale.order_number,
                        product_id=item.product_id,
                        warehouse_id=item.warehouse_id,
                        delivery_stop_id=db_delivery_stop.id,
                    )
            uow.commit()
            return True
        except IntegrityError as e:
            uow.rollback()
            print(f"Duplicate entry found: {e.orig}")
            return True
        except Exception as e:
            uow.rollback()
            print(f"Error creating delivery items: {e}")
            return False


def create_delivery_transaction(
    db: Session, request: schemas.DeliveryCreateRequestSchema
) -> List[models.Delivery]:
    """Create delivery transactions based on sales orders pending delivery."""
    pending_delivery_stops = get_stops_pending_to_delivery(
        db, request.warehouse_id
    )
    if not pending_delivery_stops:
        return []

    with unit_of_work(db) as uow:
        try:

            created_deliveries = []
            stops_by_warehouse = group_stops_by_warehouse(
                pending_delivery_stops
            )
            for warehouse_id, stop_ids in stops_by_warehouse.items():
                # Divide stops into chunks of 10
                stop_chunks = [
                    stop_ids[i : i + 10] for i in range(0, len(stop_ids), 10)
                ]

                # Create a delivery for each chunk
                for chunk in stop_chunks:
                    db_delivery = uow.delivery.create(warehouse_id)

                    result = uow.delivery_stop.update_delivery_assignment(
                        db_delivery.id,
                        chunk,
                    )
                    if result == 0:
                        uow.rollback()
                        return created_deliveries

                    driver = get_driver_available(db, request.delivery_date)
                    if driver:
                        update_driver_on_delivery(
                            db,
                            db_delivery.id,
                            driver.id,
                            request.delivery_date,
                        )
                    else:
                        print(
                            f"No available driver for delivery {db_delivery.id}"
                        )
                        uow.rollback()
                        return created_deliveries
                    uow.commit()
                    created_deliveries.append(db_delivery)

            return created_deliveries
        except Exception as e:
            uow.rollback()
            print(f"Error creating deliveries: {e}")
            return []
