import re
import random
import pytest
from typing import Dict
from faker import Faker
from fastapi.testclient import TestClient

fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def fake_warehouse() -> Dict:
    """Generate fake warehouse data"""

    phone_length = random.randint(7, 10)
    phone_digits = ''.join(
        [str(random.randint(0, 9)) for _ in range(phone_length)]
    )
    phone = int(phone_digits) if random.choice([True, False]) else phone_digits

    return {
        "warehouse_name": re.sub(r'[^a-zA-Z0-9_ñÑ]', ' ', fake.company()),
        "country": fake.country(),
        "city": fake.city(),
        "address": fake.address().replace("\n", ", "),
        "phone": phone,
    }


def test_create_warehouse_success(
    client: TestClient, fake_warehouse: Dict
) -> None:
    """Test creating a new warehouse"""

    # Act
    response = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["warehouse_name"] == fake_warehouse["warehouse_name"]
    assert response_data["warehouse_id"] is not None


def test_create_warehouse_failed_with_invalid_phone_format(
    client: TestClient, fake_warehouse: Dict
) -> None:
    """Test creating a new warehouse"""
    # Arrange
    fake_warehouse["phone"] = fake.phone_number()

    # Act
    response = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Assert
    assert response.status_code == 400


def test_create_warehouse_failed_with_oversized_phone_number(
    client: TestClient, fake_warehouse: Dict
) -> None:
    """Test creating a new warehouse"""
    # Arrange
    fake_warehouse["phone"] = ''.join(
        [str(random.randint(0, 9)) for _ in range(11)]
    )

    # Act
    response = client.post("/inventory/warehouse/", json=fake_warehouse)

    # Assert
    assert response.status_code == 400


def test_list_warehouses(client: TestClient, fake_warehouse: Dict):
    """Test listing warehouses with filters"""
    # Act
    warehouse = client.post("/inventory/warehouse", json=fake_warehouse)

    # Test without filters
    response = client.get("/inventory/warehouse")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

    # Test with name filter
    response = client.get(
        f"/inventory/warehouse?name={fake_warehouse['warehouse_name']}"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

    # Test with id filter
    response = client.get(
        f"/inventory/warehouse?id={warehouse.json()['warehouse_id']}"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_single_warehouse(client: TestClient, fake_warehouse: Dict):
    """Test getting a single warehouse by ID"""
    # Act
    warehouse = client.post("/inventory/warehouse", json=fake_warehouse)

    # Test warehouse found
    response = client.get(
        f"/inventory/warehouse/{warehouse.json()['warehouse_id']}"
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["warehouse_id"] == warehouse.json()["warehouse_id"]
    assert response_data["warehouse_name"] == fake_warehouse["warehouse_name"]

    # Test warehouse not found
    response = client.get("/inventory/warehouse/999")
    assert response.status_code != 200
