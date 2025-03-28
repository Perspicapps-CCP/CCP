from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient

fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def manufacturer_payload() -> Dict:
    """
    Fixture to generate a sample payload for creating a delivery.
    """
    return {
        "manufacturer_name": fake.name(),
        "identification_type":  "CC",
        "identification_number": str(fake.random_number(digits=10)) ,
        "address": fake.address(),
        "contact_phone": str(fake.random_number(digits=10)),
        "email":  fake.email()
    }


def test_create_manufacturer(client: TestClient, manufacturer_payload: Dict) -> None:
    """
    Test the creation of a manufacturer.
    """
    response = client.post("/suppliers/manufacturers", json=manufacturer_payload)
    assert response.status_code == 200    
    assert response.json()["id"] is not None, "ID cannot be null"
    
def test_create_manufacturer_invalid_id_type(client: TestClient, manufacturer_payload: Dict) -> None:
    """
    Test the creation of a manufacturer with invalide id type.
    """
    manufacturer_payload["identification_type"] = "AA"
    response = client.post("/suppliers/manufacturers", json=manufacturer_payload)
    assert response.status_code == 422        
    
def test_create_manufacturer_invalid_email(client: TestClient, manufacturer_payload: Dict) -> None:
    """
    Test the creation of a manufacturer with invalide id type.
    """
    manufacturer_payload["email"] = "abc123"
    response = client.post("/suppliers/manufacturers", json=manufacturer_payload)
    assert response.status_code == 422   
