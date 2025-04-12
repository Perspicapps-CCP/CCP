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


def test_list_all_deliveries(client: TestClient) -> None:
    """
    Test listing all deliveries.
    """
    response = client.get("/logistic/delivery/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

