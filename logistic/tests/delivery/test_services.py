import datetime
import uuid
from uuid import UUID
from faker import Faker
from delivery import models, services
from delivery.schemas import (
    DriverCreateSchema,
    PayloadAddressSchema,
    PayloadSaleSchema,
    PayloadSaleItemSchema,
)

fake = Faker()
fake.seed_instance(123)


def fake_address():
    return PayloadAddressSchema(
        id=uuid.uuid4(),
        street=fake.address(),
        city=fake.city(),
        state=fake.state(),
        postal_code=fake.postcode(),
        country=fake.country(),
    )


def test_group_items_by_warehouse_empty_list():
    """
    Test grouping items when there are no items.
    """
    dummy_address = fake_address()

    # Create a sale with no items
    sale = PayloadSaleSchema(
        sales_id=UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[],
    )

    # Call the function
    result = services.group_items_by_warehouse(sale)

    # Verify result is an empty dict
    assert result == {}


def test_group_items_by_warehouse_single_warehouse():
    """
    Test grouping items when all items are from the same warehouse.
    """
    dummy_address = fake_address()

    warehouse_id = UUID("11111111-1234-5678-1234-567812345678")
    sale = PayloadSaleSchema(
        sales_id=UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[
            PayloadSaleItemSchema(
                sales_item_id=UUID(int=0),
                product_id=UUID("aaaaaaaa-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id,
            ),
            PayloadSaleItemSchema(
                sales_item_id=UUID(int=0),
                product_id=UUID("bbbbbbbb-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id,
            ),
        ],
    )

    # Call the function
    result = services.group_items_by_warehouse(sale)

    # Verify result contains the single warehouse and all items
    assert len(result) == 1
    assert warehouse_id in result
    assert len(result[warehouse_id]) == 2
    assert result[warehouse_id][0].product_id == UUID(
        "aaaaaaaa-1234-5678-1234-567812345678"
    )
    assert result[warehouse_id][1].product_id == UUID(
        "bbbbbbbb-1234-5678-1234-567812345678"
    )


def test_group_items_by_warehouse_multiple_warehouses():
    """
    Test grouping items when items are from multiple warehouses.
    """
    dummy_address = fake_address()
    # Create a sale with items from multiple warehouses
    warehouse_id1 = UUID("11111111-1234-5678-1234-567812345678")
    warehouse_id2 = UUID("22222222-1234-5678-1234-567812345678")

    sale = PayloadSaleSchema(
        sales_id=UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[
            PayloadSaleItemSchema(
                sales_item_id=UUID(int=0),
                product_id=UUID("aaaaaaaa-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id1,
            ),
            PayloadSaleItemSchema(
                sales_item_id=UUID(int=0),
                product_id=UUID("bbbbbbbb-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id2,
            ),
            PayloadSaleItemSchema(
                sales_item_id=UUID(int=0),
                product_id=UUID("cccccccc-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id1,
            ),
        ],
    )

    # Call the function
    result = services.group_items_by_warehouse(sale)

    # Verify result contains both warehouses with correct items
    assert len(result) == 2
    assert warehouse_id1 in result
    assert warehouse_id2 in result

    # Verify warehouse_id1 has two items with correct product IDs
    assert len(result[warehouse_id1]) == 2
    assert result[warehouse_id1][0].product_id == UUID(
        "aaaaaaaa-1234-5678-1234-567812345678"
    )
    assert result[warehouse_id1][1].product_id == UUID(
        "cccccccc-1234-5678-1234-567812345678"
    )

    # Verify warehouse_id2 has one item with correct product ID
    assert len(result[warehouse_id2]) == 1
    assert result[warehouse_id2][0].product_id == UUID(
        "bbbbbbbb-1234-5678-1234-567812345678"
    )


def test_group_stops_by_warehouse_empty_list():
    """
    Test grouping stops when there are no pending delivery stops.
    """
    # Empty list of pending delivery stops
    pending_delivery_stops = []

    # Call the function
    result = services.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result is an empty dict
    assert result == {}


def test_group_stops_by_warehouse_single_warehouse():
    """
    Test grouping stops when all stops are from the same warehouse.
    """
    # Create pending delivery stops with a single warehouse
    warehouse_id = UUID("11111111-1234-5678-1234-567812345678")
    stop_id1 = UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = UUID("bbbbbbbb-1234-5678-1234-567812345678")
    sales_id = UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id),
        (stop_id2, sales_id, warehouse_id),
    ]

    # Call the function
    result = services.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result contains the single warehouse and all stops
    assert len(result) == 1
    assert warehouse_id in result
    assert len(result[warehouse_id]) == 2
    assert stop_id1 in result[warehouse_id]
    assert stop_id2 in result[warehouse_id]


def test_group_stops_by_warehouse_multiple_warehouses():
    """
    Test grouping stops when stops are from multiple warehouses.
    """
    # Create pending delivery stops from multiple warehouses
    warehouse_id1 = UUID("11111111-1234-5678-1234-567812345678")
    warehouse_id2 = UUID("22222222-1234-5678-1234-567812345678")

    stop_id1 = UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = UUID("bbbbbbbb-1234-5678-1234-567812345678")
    stop_id3 = UUID("cccccccc-1234-5678-1234-567812345678")

    sales_id = UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id1),
        (stop_id2, sales_id, warehouse_id2),
        (stop_id3, sales_id, warehouse_id1),
    ]

    # Call the function
    result = services.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result contains both warehouses with correct stops
    assert len(result) == 2
    assert warehouse_id1 in result
    assert warehouse_id2 in result

    # Verify warehouse_id1 has two stops
    assert len(result[warehouse_id1]) == 2
    assert stop_id1 in result[warehouse_id1]
    assert stop_id3 in result[warehouse_id1]

    # Verify warehouse_id2 has one stop
    assert len(result[warehouse_id2]) == 1
    assert stop_id2 in result[warehouse_id2]


def test_group_stops_by_warehouse_preserve_order():
    """
    Test that the order of stops is preserved within each warehouse group.
    """
    # Create pending delivery stops with specific order
    warehouse_id = UUID("11111111-1234-5678-1234-567812345678")
    stop_id1 = UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = UUID("bbbbbbbb-1234-5678-1234-567812345678")
    stop_id3 = UUID("cccccccc-1234-5678-1234-567812345678")
    sales_id = UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id),
        (stop_id2, sales_id, warehouse_id),
        (stop_id3, sales_id, warehouse_id),
    ]

    # Call the function
    result = services.group_stops_by_warehouse(pending_delivery_stops)

    # Verify the order is preserved
    assert result[warehouse_id] == [stop_id1, stop_id2, stop_id3]


def test_create_order_delivery_integration(db_session):
    """
    Test creating a delivery order with a warehouse ID using a real database session.
    This test verifies that the function correctly creates and returns a Delivery object.
    """
    # Create test data
    warehouse_id = uuid.uuid4()

    # Call the function
    result = services.create_order_delivery(db_session, warehouse_id)

    # Verify the result is a Delivery object with the correct warehouse_id
    assert isinstance(result, models.Delivery)
    assert result.warehouse_id == warehouse_id
    assert result.id is not None  # Ensure an ID was assigned
    assert result.driver_id is None  # Should be None by default
    assert result.delivery_date is None  # Should be None by default
    assert result.status == models.DeliverStatus.CREATED  # Default status


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
