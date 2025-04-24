import uuid
import pytest
from unittest.mock import MagicMock
from faker import Faker
from fastapi.testclient import TestClient

from deliveries import models
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker()
fake.seed_instance(0)


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
        address_id=uuid.uuid4(),
        address=fake.address(),
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
    delivery_stop.address_id = address.address_id
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
