from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient

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


def test_create_delivery(client: TestClient, delivery_payload: Dict) -> None:
    """
    Test the creation of a delivery.
    """
    response = client.post("/logistica/entregas/", json=delivery_payload)
    assert response.status_code == 200
    assert response.json()["purchase_id"] == delivery_payload["purchase_id"]


def test_get_delivery(client: TestClient, delivery_payload: Dict) -> None:
    """
    Test retrieving a delivery by its ID.
    """
    # First, create a delivery
    create_response = client.post(
        "/logistica/entregas/", json=delivery_payload
    )
    delivery_id = create_response.json()["id"]

    # Then, get the delivery
    response = client.get(f"/logistica/entregas/{delivery_id}")
    assert response.status_code == 200
    assert response.json()["id"] == delivery_id


def test_list_all_deliveries(client: TestClient) -> None:
    """
    Test listing all deliveries.
    """
    response = client.get("/logistica/entregas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_delivery(client: TestClient, delivery_payload: Dict) -> None:
    """
    Test deleting a delivery by its ID.
    """
    # First, create a delivery
    create_response = client.post(
        "/logistica/entregas/", json=delivery_payload
    )
    delivery_id = create_response.json()["id"]

    # Then, delete the delivery
    response = client.delete(f"/logistica/entregas/{delivery_id}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Todos los datos fueron eliminados"

    # Verify the delivery is deleted
    get_response = client.get(f"/logistica/entregas/{delivery_id}")
    assert get_response.status_code == 404
