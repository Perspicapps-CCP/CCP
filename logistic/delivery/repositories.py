from datetime import datetime
from typing import Dict, Generator, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, update
from sqlalchemy.orm import Session, joinedload

from delivery import models, schemas


class DeliveryRepository:
    """Repository class for delivery-related database operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> Generator[models.Delivery, None, None]:
        """Get all deliveries with associated drivers."""
        query = (
            self.session.query(models.Delivery)
            .options(joinedload(models.Delivery.driver))
            .join(models.Driver, models.Driver.id == models.Delivery.driver_id)
            .yield_per(100)
        )
        for delivery in query:
            yield delivery

    def get_by_id(self, delivery_id: UUID) -> Optional[models.Delivery]:
        """Get a specific delivery by ID."""
        query = self.session.query(models.Delivery).filter(
            models.Delivery.id == delivery_id
        )
        return query.first()

    def get_by_ids(self, delivery_ids: List[UUID]) -> List[models.Delivery]:
        """Get deliveries by a list of IDs."""
        query = self.session.query(models.Delivery).filter(
            models.Delivery.id.in_(delivery_ids)
        )
        return query.all()

    def get_without_stops_ordered(self) -> List[models.Delivery]:
        """Get deliveries without ordered stops."""
        query = (
            self.session.query(models.Delivery)
            .options(
                joinedload(models.Delivery.stops).joinedload(
                    models.DeliveryStop.address
                )
            )
            .join(
                models.DeliveryStop,
                models.Delivery.id == models.DeliveryStop.delivery_id,
            )
            .filter(models.DeliveryStop.order_stop == 0)
        )
        return query.all()

    def get_route(
        self, delivery_id: UUID
    ) -> List[
        Tuple[models.Delivery, models.DeliveryStop, models.DeliveryAddress]
    ]:
        """Get the route for a specific delivery."""
        query = (
            self.session.query(
                models.Delivery, models.DeliveryStop, models.DeliveryAddress
            )
            .join(
                models.DeliveryStop,
                models.Delivery.id == models.DeliveryStop.delivery_id,
            )
            .join(
                models.DeliveryAddress,
                models.DeliveryStop.address_id == models.DeliveryAddress.id,
            )
            .filter(models.Delivery.id == delivery_id)
            .order_by(models.DeliveryStop.order_stop)
        )
        return query.all()

    def create(self, warehouse_id: UUID) -> models.Delivery:
        """Create a new delivery for a specific warehouse."""
        db_delivery = models.Delivery(
            warehouse_id=warehouse_id,
        )
        self.session.add(db_delivery)
        self.session.flush()
        self.session.refresh(db_delivery)
        return db_delivery

    def update_driver(
        self, delivery_id: UUID, driver_id: UUID, delivery_date: datetime
    ) -> bool:
        """Update driver and date for a delivery."""
        update_query = (
            update(models.Delivery)
            .values(
                driver_id=driver_id,
                delivery_date=delivery_date,
                status=models.DeliverStatus.SCHEDULED,
            )
            .where(models.Delivery.id == delivery_id)
        )
        result = self.session.execute(update_query)
        return result.rowcount > 0


class DeliveryItemRepository:
    """Repository class for delivery item operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_delivery_id(
        self, delivery_id: UUID
    ) -> Generator[Tuple, None, None]:
        """Get all items for a specific delivery."""
        query = (
            self.session.query(
                models.DeliveryItem,
                func.concat_ws(
                    ", ",
                    models.DeliveryAddress.street,
                    models.DeliveryAddress.city,
                    models.DeliveryAddress.state,
                    models.DeliveryAddress.country,
                ).label("delivery_address"),
            )
            .join(
                models.DeliveryStop,
                models.DeliveryStop.id == models.DeliveryItem.delivery_stop_id,
            )
            .join(
                models.DeliveryAddress,
                models.DeliveryAddress.id == models.DeliveryStop.address_id,
            )
            .filter(models.DeliveryStop.delivery_id == delivery_id)
            .yield_per(100)
        )
        for delivery_item in query:
            yield delivery_item

    def create(
        self,
        sales_id: UUID,
        order_number: int,
        product_id: UUID,
        warehouse_id: UUID,
        delivery_stop_id: UUID,
        quantity: int = 1,
    ) -> models.DeliveryItem:
        """Create a new delivery item."""
        db_delivery_item = models.DeliveryItem(
            sales_id=sales_id,
            order_number=order_number,
            product_id=product_id,
            warehouse_id=warehouse_id,
            delivery_stop_id=delivery_stop_id,
            quantity=quantity,
        )
        self.session.add(db_delivery_item)
        self.session.flush()
        self.session.refresh(db_delivery_item)
        return db_delivery_item


class DeliveryStopRepository:
    """Repository class for delivery stop operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_pending_stops(
        self, warehouse_id: UUID
    ) -> List[Tuple[UUID, UUID, UUID]]:
        """Get stops pending assignment to deliveries."""
        query = (
            self.session.query(
                models.DeliveryStop.id,
                models.DeliveryItem.sales_id,
                models.DeliveryItem.warehouse_id,
            )
            .join(
                models.DeliveryItem,
                models.DeliveryItem.delivery_stop_id == models.DeliveryStop.id,
            )
            .distinct()
            .filter(
                and_(
                    models.DeliveryStop.delivery_id.is_(None),
                    models.DeliveryItem.warehouse_id == warehouse_id,
                )
            )
        )

        return query.all()

    def create(
        self, sales_id: UUID, order_number: int, address_id: UUID
    ) -> models.DeliveryStop:
        """Create a new delivery stop."""
        db_delivery_stop = models.DeliveryStop(
            sales_id=sales_id,
            order_number=order_number,
            address_id=address_id,
        )
        self.session.add(db_delivery_stop)
        self.session.flush()
        self.session.refresh(db_delivery_stop)
        return db_delivery_stop

    def update_delivery_assignment(
        self, delivery_id: UUID, stop_ids: List[UUID]
    ) -> int:
        """Update delivery assignment for specified stops."""
        update_query = (
            update(models.DeliveryStop)
            .values(delivery_id=delivery_id)
            .where(
                and_(
                    models.DeliveryStop.id.in_(stop_ids),
                    models.DeliveryStop.delivery_id == None,  # noqa: E711
                )
            )
        )
        result = self.session.execute(update_query)
        return result.rowcount

    def update_stop_order(self, list_stop_id: List[Dict]) -> bool:
        """Update the order of delivery stops."""
        for index, stop_id in enumerate(list_stop_id):
            update_query = (
                update(models.DeliveryStop)
                .values(order_stop=index + 1)
                .where(models.DeliveryStop.id == stop_id["stop"])
            )
            result = self.session.execute(update_query)
            if result.rowcount == 0:
                return False
        return True


class DeliveryAddressRepository:
    """Repository class for delivery address operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_without_geocoding(self) -> List[models.DeliveryAddress]:
        """Get addresses without geocoding information."""
        query = (
            self.session.query(models.DeliveryAddress)
            .filter(
                (models.DeliveryAddress.latitude.is_(None))
                | (models.DeliveryAddress.longitude.is_(None))
            )
            .limit(100)
        )
        return query.all()

    def create(
        self, delivery_address: schemas.PayloadAddressSchema
    ) -> models.DeliveryAddress:
        """Create a new delivery address."""
        db_delivery_address = models.DeliveryAddress(
            id=delivery_address.id,
            street=delivery_address.street,
            city=delivery_address.city,
            state=delivery_address.state,
            postal_code=delivery_address.postal_code,
            country=delivery_address.country,
        )
        self.session.add(db_delivery_address)
        self.session.flush()
        self.session.refresh(db_delivery_address)
        return db_delivery_address

    def get_by_id(self, address_id: UUID) -> Optional[models.DeliveryAddress]:
        """Get a specific delivery address by ID."""
        query = self.session.query(models.DeliveryAddress).filter(
            models.DeliveryAddress.id == address_id
        )
        return query.first()


class DriverRepository:
    """Repository class for driver operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_available(
        self, delivery_date: datetime
    ) -> Optional[models.Driver]:
        """Get the first available driver on a specific date."""
        return (
            self.session.query(models.Driver)
            .outerjoin(
                models.Delivery,
                and_(
                    models.Delivery.driver_id == models.Driver.id,
                    models.Delivery.delivery_date == delivery_date,
                ),
            )
            .filter(models.Delivery.id == None)  # noqa: E711
            .first()
        )

    def create(self, driver: schemas.DriverCreateSchema) -> models.Driver:
        """Create a new driver."""
        db_driver = models.Driver(
            name=driver.driver_name,
            license_plate=driver.license_plate,
            phone_number=driver.phone_number,
        )
        self.session.add(db_driver)
        self.session.flush()
        self.session.refresh(db_driver)
        return db_driver
