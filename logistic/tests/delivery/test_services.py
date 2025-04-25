import datetime
import uuid
from faker import Faker
from delivery import models, services
from delivery.schemas import DriverCreateSchema

fake = Faker()
fake.seed_instance(123)


def test_create_driver_success(db_session):
    """
    Test that create_driver correctly creates a new driver with the provided information.
    """
    # Create a mock driver schema
    driver_schema = DriverCreateSchema(
        driver_name="John Doe", license_plate="ABC123", phone_number="5551234"
    )

    # Call the function
    result = services.create_driver(db_session, driver_schema)

    # Verify the result is a Driver object with the correct attributes
    assert isinstance(result, models.Driver)
    assert result.name == "John Doe"
    assert result.license_plate == "ABC123"
    assert result.phone_number == "5551234"
    assert result.id is not None  # Ensure an ID was assigned


def test_get_driver_available_driver_available(db_session):
    """
    Test that get_driver_available returns a driver when one is available.
    """
    # Set up test data - one available driver
    driver = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    db_session.add(driver)
    db_session.commit()

    delivery_date = datetime.datetime(2023, 5, 1)

    # Call the function
    result = services.get_driver_available(db_session, delivery_date)

    # Verify the correct driver is returned
    assert result is not None
    assert result.id == driver.id
    assert result.name == "John Doe"
    assert result.license_plate == "ABC123"


def test_get_driver_available_driver_busy(db_session):
    """
    Test that get_driver_available does not return a driver who is already assigned
    to a delivery on the specified date.
    """
    # Set up test data - one driver with assigned delivery
    driver = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    db_session.add(driver)
    db_session.flush()

    delivery_date = datetime.datetime(2023, 5, 1)

    # Create a delivery assigned to the driver on the date
    delivery = models.Delivery(
        warehouse_id=uuid.uuid4(),
        driver_id=driver.id,
        delivery_date=delivery_date,
        status=models.DeliverStatus.SCHEDULED,
    )
    db_session.add(delivery)
    db_session.commit()

    # Call the function
    result = services.get_driver_available(db_session, delivery_date)

    # Verify no driver is returned
    assert result is None


def test_get_driver_available_multiple_drivers(db_session):
    """
    Test that get_driver_available returns the first available driver
    when multiple drivers are available.
    """
    # Set up test data - multiple available drivers
    driver1 = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    driver2 = models.Driver(
        name="Jane Smith", license_plate="XYZ789", phone_number="5555678"
    )
    db_session.add_all([driver1, driver2])
    db_session.commit()

    delivery_date = datetime.datetime(2023, 5, 1)

    # Call the function
    result = services.get_driver_available(db_session, delivery_date)

    # Verify the first driver is returned
    assert result is not None
    assert result.id == driver1.id
    assert result.name == "John Doe"


def test_get_driver_available_some_drivers_busy(db_session):
    """
    Test that get_driver_available returns only drivers who are not assigned
    to deliveries on the specified date.
    """
    # Set up test data - one busy driver, one available
    driver_busy = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    driver_available = models.Driver(
        name="Jane Smith", license_plate="XYZ789", phone_number="5555678"
    )
    db_session.add_all([driver_busy, driver_available])
    db_session.flush()

    delivery_date = datetime.datetime(2023, 5, 1)

    # Create a delivery assigned to the first driver
    delivery = models.Delivery(
        warehouse_id=uuid.uuid4(),
        driver_id=driver_busy.id,
        delivery_date=delivery_date,
        status=models.DeliverStatus.SCHEDULED,
    )
    db_session.add(delivery)
    db_session.commit()

    # Call the function
    result = services.get_driver_available(db_session, delivery_date)

    # Verify the available driver is returned
    assert result is not None
    assert result.id == driver_available.id
    assert result.name == "Jane Smith"


def test_get_driver_available_different_dates(db_session):
    """
    Test that a driver assigned to a delivery on one date is still
    available on a different date.
    """
    # Set up test data - one driver
    driver = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    db_session.add(driver)
    db_session.flush()

    # Create a delivery assigned to the driver on May 1st
    busy_date = datetime.datetime(2023, 5, 1)
    delivery = models.Delivery(
        warehouse_id=uuid.uuid4(),
        driver_id=driver.id,
        delivery_date=busy_date,
        status=models.DeliverStatus.SCHEDULED,
    )
    db_session.add(delivery)
    db_session.commit()

    # Check driver's availability on May 2nd
    available_date = datetime.datetime(2023, 5, 2)
    result = services.get_driver_available(db_session, available_date)

    # Verify the driver is available on May 2nd
    assert result is not None
    assert result.id == driver.id
    assert result.name == "John Doe"

    # Double-check driver is not available on May 1st
    result_busy = services.get_driver_available(db_session, busy_date)
    assert result_busy is None


