from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient

fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def fake_warehouse() -> Dict:
    """Generate fake warehouse data"""
    return {
        "warehouse_name": fake.company(),
        "country": fake.country(),
        "city": fake.city(),
        "address": fake.address().replace("\n", ", "),
        "phone": fake.phone_number(),
    }


def test_create_warehouse(client: TestClient, fake_warehouse: Dict) -> None:
    """Test creating a new warehouse"""
    # Make request
    response = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Assert response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["warehouse_name"] == fake_warehouse["warehouse_name"]
    assert response_data["warehouse_id"] is not None


def test_list_warehouses(client: TestClient, fake_warehouse: Dict):
    """Test listing warehouses with filters"""
    # Arrange
    warehouse = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Test without filters
    response = client.get("/inventory/warehouse/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

    # Test with name filter
    response = client.get(
        f"/inventory/warehouse/?name={fake_warehouse['warehouse_name']}"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

    # Test with id filter
    response = client.get(
        f"/inventory/warehouse/?id={warehouse.json()['warehouse_id']}"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_single_warehouse(client: TestClient, fake_warehouse: Dict):
    """Test getting a single warehouse by ID"""
    # Arrange
    warehouse = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Test warehouse found
    response = client.get(f"/inventory/warehouse/{warehouse.json()['warehouse_id']}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["warehouse_id"] == warehouse.json()["warehouse_id"]
    assert response_data["warehouse_name"] == fake_warehouse["warehouse_name"]

    # Test warehouse not found
    response = client.get("/inventory/warehouse/999")
    assert response.status_code != 200
