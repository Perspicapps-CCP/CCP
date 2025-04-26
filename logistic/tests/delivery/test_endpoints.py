import uuid
import pytest
from unittest.mock import MagicMock
from faker import Faker
from fastapi.testclient import TestClient

from delivery import models
from rpc_clients import schemas
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker()
fake.seed_instance(123)


@pytest.fixture
def mock_suppliers_client():
    mock_client = MagicMock()
    mock_client.get_all_products.return_value = []
    return mock_client


@pytest.fixture
def mock_inventory_client():
    mock_client = MagicMock()
    mock_client.get_warehouses.return_value = []
    return mock_client


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
        latitude=fake.latitude(),
        longitude=fake.longitude(),
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
        address_id=uuid.uuid4(),
        delivery_id=uuid.uuid4(),
    )


def dummy_delivery():
    return models.Delivery(
        id=uuid.uuid4(),
        driver_id=uuid.uuid4(),
        warehouse_id=uuid.uuid4(),
    )


def test_list_all_deliveries_with_product_and_warehouse_empty(
    client: TestClient, mock_suppliers_client, mock_inventory_client
) -> None:
    """
    Test listing all deliveries.
    """
    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    client.app.dependency_overrides[InventoryClient] = (
        lambda: mock_inventory_client
    )

    response = client.get("/logistic/delivery/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_all_deliveries_with_product_and_warehouse_exist(
    client: TestClient,
    db_session,
    mock_suppliers_client,
    mock_inventory_client,
) -> None:
    """
    Test listing all deliveries.
    """
    address = dummy_address()
    driver = dummy_driver()
    db_session.add(address)
    db_session.add(driver)
    db_session.flush()

    delivery_item = dummy_delivery_item()
    delivery_stop = dummy_delivery_stop()
    delivery = dummy_delivery()
    delivery.driver_id = driver.id
    delivery.warehouse_id = delivery_item.warehouse_id
    db_session.add(delivery)
    db_session.flush()

    delivery_stop.sales_id = delivery_item.sales_id
    delivery_stop.order_number = delivery_item.order_number
    delivery_stop.address_id = address.id
    delivery_stop.delivery_id = delivery.id
    db_session.add(delivery_stop)
    db_session.flush()

    delivery_item.delivery_stop_id = delivery_stop.id
    db_session.add(delivery_item)
    db_session.commit()

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    client.app.dependency_overrides[InventoryClient] = (
        lambda: mock_inventory_client
    )

    response = client.get("/logistic/delivery/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_delivery_route(
    client: TestClient,
    db_session,
    mock_inventory_client,
) -> None:
    """
    Test getting a delivery route.
    """
    address_1 = dummy_address()
    address_2 = dummy_address()
    driver = dummy_driver()
    db_session.add(address_1)
    db_session.add(address_2)
    db_session.add(driver)
    db_session.flush()

    delivery = dummy_delivery()
    delivery.driver_id = driver.id
    delivery.warehouse_id = uuid.uuid4()
    db_session.add(delivery)
    db_session.flush()

    delivery_stop_1 = dummy_delivery_stop()
    delivery_stop_1.sales_id = uuid.uuid4()
    delivery_stop_1.order_number = fake.random_int()
    delivery_stop_1.address_id = address_1.id
    delivery_stop_1.delivery_id = delivery.id
    db_session.add(delivery_stop_1)

    delivery_stop_2 = dummy_delivery_stop()
    delivery_stop_2.sales_id = uuid.uuid4()
    delivery_stop_2.order_number = fake.random_int()
    delivery_stop_2.address_id = address_2.id
    delivery_stop_2.delivery_id = delivery.id
    db_session.add(delivery_stop_2)
    db_session.commit()

    mock_inventory_client.get_warehouses.return_value = [
        schemas.WarehouseSchema(
            warehouse_id=delivery.warehouse_id,
            warehouse_name=fake.company(),
            address=fake.address(),
            phone=fake.phone_number(),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
        )
    ]

    client.app.dependency_overrides[InventoryClient] = (
        lambda: mock_inventory_client
    )

    response = client.get(f"/logistic/route/{delivery.id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
