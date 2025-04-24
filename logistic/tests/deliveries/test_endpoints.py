import pytest
from typing import Dict
from unittest.mock import MagicMock
from faker import Faker
from fastapi.testclient import TestClient

from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def delivery_payload() -> Dict:
    """
    Fixture to generate a sample payload for creating a delivery.
    """
    return {
        "purchase_id": fake.uuid4(),
        "address_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "items": [
            {
                "product_id": fake.uuid4(),
                "quantity": fake.random_int(min=1, max=10),
            },
            {
                "product_id": fake.uuid4(),
                "quantity": fake.random_int(min=1, max=10),
            },
        ],
    }


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


def test_list_all_deliveries(
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
