import datetime
import random
from typing import List
import uuid
from faker import Faker
from delivery import models, services
from delivery import schemas
from delivery.schemas import DriverCreateSchema

fake = Faker()
fake.seed_instance(123)


def dummy_driver():
    return models.Driver(
        name=fake.name(),
        license_plate=fake.license_plate(),
        phone_number=fake.phone_number(),
    )


def dummy_address():
    return models.DeliveryAddress(
        id=uuid.uuid4(),
        street=fake.address(),
        city=fake.city(),
        state=fake.state(),
        postal_code=fake.postcode(),
        country=fake.country(),
    )


def dummy_delivery_item():
    return models.DeliveryItem(
        sales_id=uuid.uuid4(),
        order_number=fake.random_int(),
        product_id=uuid.uuid4(),
        warehouse_id=uuid.uuid4(),
    )


def dummy_delivery_stop():
    return models.DeliveryStop(
        sales_id=uuid.uuid4(),
        order_number=uuid.uuid4(),
    )


def dummy_delivery():
    return models.Delivery(
        id=uuid.uuid4(),
        driver_id=uuid.uuid4(),
        warehouse_id=uuid.uuid4(),
    )


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
    # Arrange
    driver = models.Driver(
        name="John Doe", license_plate="ABC123", phone_number="5551234"
    )
    db_session.add(driver)
    db_session.flush()

    busy_date = datetime.datetime(2023, 5, 1)
    delivery = models.Delivery(
        warehouse_id=uuid.uuid4(),
        driver_id=driver.id,
        delivery_date=busy_date,
        status=models.DeliverStatus.SCHEDULED,
    )
    db_session.add(delivery)
    db_session.commit()

    # Act
    available_date = datetime.datetime(2023, 5, 2)
    result = services.get_driver_available(db_session, available_date)

    # Assert
    assert result is not None
    assert result.id == driver.id
    assert result.name == "John Doe"

    # Act
    result_busy = services.get_driver_available(db_session, busy_date)

    # Assert
    assert result_busy is None


def test_create_delivery_stops_transaction_success(db_session):
    # Arrange
    delivery_item = schemas.PayloadSaleItemSchema(
        sales_item_id=fake.uuid4(),
        product_id=fake.uuid4(),
        warehouse_id=fake.uuid4(),
    )

    address = schemas.PayloadAddressSchema(
        id=fake.uuid4(),
        street=f"Calle {random.randint(1, 150)} #{random.randint(1, 120)}-{random.randint(1, 99)}",
        city="Bogotá",
        state="Bogotá D.C.",
        postal_code="110000",
        country="Colombia",
    )
    delivery = schemas.PayloadSaleSchema(
        sales_id=fake.uuid4(),
        order_number=random.randint(1, 150),
        address=address,
        sales_items=[delivery_item],
    )

    # Act
    result = services.create_delivery_stops_transaction(db_session, delivery)

    # Assert
    assert result is True


def test_create_duplicate_delivery_stops_transaction_success(db_session):
    # Arrange
    delivery_item = schemas.PayloadSaleItemSchema(
        sales_item_id=fake.uuid4(),
        product_id=fake.uuid4(),
        warehouse_id=fake.uuid4(),
    )

    address = schemas.PayloadAddressSchema(
        id=fake.uuid4(),
        street=f"Calle {random.randint(1, 150)} #{random.randint(1, 120)}-{random.randint(1, 99)}",
        city="Bogotá",
        state="Bogotá D.C.",
        postal_code="110000",
        country="Colombia",
    )
    delivery = schemas.PayloadSaleSchema(
        sales_id=fake.uuid4(),
        order_number=random.randint(1, 150),
        address=address,
        sales_items=[delivery_item],
    )

    # Act
    services.create_delivery_stops_transaction(db_session, delivery)
    result = services.create_delivery_stops_transaction(db_session, delivery)

    # Assert
    assert result is True


def test_create_delivery_transaction_success(db_session):
    # Arrange
    address = dummy_address()
    driver = dummy_driver()
    db_session.add(address)
    db_session.add(driver)
    db_session.flush()

    delivery_item = dummy_delivery_item()
    delivery_stop = dummy_delivery_stop()
    delivery_stop.sales_id = delivery_item.sales_id
    delivery_stop.order_number = delivery_item.order_number
    delivery_stop.address_id = address.id
    db_session.add(delivery_stop)
    db_session.flush()

    delivery_item.delivery_stop_id = delivery_stop.id
    db_session.add(delivery_item)
    db_session.commit()

    # Act
    request = schemas.DeliveryCreateRequestSchema(
        delivery_date=datetime.datetime(2023, 5, 1),
        warehouse_id=delivery_item.warehouse_id,
    )
    delivery = services.create_delivery_transaction(db_session, request)

    # Assert
    assert delivery is not None
    assert isinstance(delivery, List)
    assert len(delivery) == 1
    delivery = delivery[0]
    assert delivery.id is not None
    assert delivery.driver_id == driver.id
    assert delivery.warehouse_id == delivery_item.warehouse_id
    assert delivery.delivery_date.date() == request.delivery_date
    assert delivery.status == models.DeliverStatus.SCHEDULED
    assert len(delivery.stops) == 1

