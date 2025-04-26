from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator, Optional, Type
from sqlalchemy.orm import Session

from .repositories import (
    DeliveryRepository,
    DeliveryItemRepository,
    DeliveryStopRepository,
    DeliveryAddressRepository,
    DriverRepository,
)


class AbstractUnitOfWork(ABC):
    """Abstract base class defining the Unit of Work interface."""

    delivery: DeliveryRepository = None
    delivery_item: DeliveryItemRepository = None
    delivery_stop: DeliveryStopRepository = None
    delivery_address: DeliveryAddressRepository = None
    driver: DriverRepository = None

    @abstractmethod
    def commit(self):
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback the current transaction."""
        pass


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """Implements the Unit of Work pattern for managing database transactions."""

    def __init__(self, session: Session):
        self.session = session
        self.delivery = DeliveryRepository(session)
        self.delivery_item = DeliveryItemRepository(session)
        self.delivery_stop = DeliveryStopRepository(session)
        self.delivery_address = DeliveryAddressRepository(session)
        self.driver = DriverRepository(session)

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()


def create_unit_of_work(session: Session) -> AbstractUnitOfWork:
    """Factory function to create a UnitOfWork instance."""
    return SQLAlchemyUnitOfWork(session)


@contextmanager
def unit_of_work(
    session: Session, uow_class: Optional[Type[AbstractUnitOfWork]] = None
) -> Generator[AbstractUnitOfWork, None, None]:
    """Context manager for the Unit of Work pattern."""
    if uow_class:
        uow = uow_class(session)
    else:
        uow = create_unit_of_work(session)

    try:
        yield uow
    except Exception:
        uow.rollback()
        raise
