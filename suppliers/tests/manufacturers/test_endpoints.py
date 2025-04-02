from typing import Dict, List
from uuid import UUID

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
        "identification_type": "CC",
        "identification_number": str(fake.random_number(digits=10)),
        "address": fake.address(),
        "contact_phone": str(fake.random_number(digits=10)),
        "email": fake.email(),
    }


@pytest.fixture
def products_ids_payload() -> Dict[str, List[str]]:
    """
    Fixture to generate a sample payload for retrieve products.
    """
    return {"productsIds": ["98765549-5fab-40bd-8076-65a05e62c808"]}


def test_create_manufacturer(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test the creation of a manufacturer.
    """
    response = client.post(
        "/suppliers/manufacturers", json=manufacturer_payload
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None, "ID cannot be null"


def test_create_manufacturer_invalid_id_type(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test the creation of a manufacturer with invalide id type.
    """
    manufacturer_payload["identification_type"] = "AA"
    response = client.post(
        "/suppliers/manufacturers", json=manufacturer_payload
    )
    assert response.status_code == 422


def test_create_manufacturer_invalid_email(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test the creation of a manufacturer with invalide id type.
    """
    manufacturer_payload["email"] = "abc123"
    response = client.post(
        "/suppliers/manufacturers", json=manufacturer_payload
    )
    assert response.status_code == 422


def test_create_manufacturer_missing_field(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test the creation of a manufacturer with em,ail missing.
    """
    del manufacturer_payload["email"]
    response = client.post(
        "/suppliers/manufacturers", json=manufacturer_payload
    )
    assert response.status_code == 422


def test_list_all_manufacturers(client: TestClient) -> None:
    """
    Test listing all maufacturers.
    """
    response = client.get("/suppliers/manufacturers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_manufacturer(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test retrieving a manufactrurer by its ID.
    """

    create_response = client.post(
        "/suppliers/manufacturers/", json=manufacturer_payload
    )
    manufacturer_id = create_response.json()["id"]

    response = client.get(f"/suppliers/manufacturers/{manufacturer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == manufacturer_id


def test_get_manufacturer_not_exists(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test try retrieving a no existing manufactrurer.
    """

    response = client.get(
        "/suppliers/manufacturers/6d17bf98-eef1-4d6d-b103-412513f3c8c6"
    )
    assert response.status_code == 404


def test_list_products_by_ids(
    client: TestClient, products_ids_payload: Dict
) -> None:
    """
    Test listing products given ids list.
    """
    response = client.post(
        "/suppliers/manufacturers/listProducts", json=products_ids_payload
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_all_products_(client: TestClient) -> None:
    """
    Test listing all products.
    """
    response = client.post("/suppliers/manufacturers/listProducts", json={})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_by_manufacturer_id(
    client: TestClient, manufacturer_payload: Dict
) -> None:
    """
    Test retrieving a product by manufactrurer ID.
    """

    create_response = client.post(
        "/suppliers/manufacturers/", json=manufacturer_payload
    )
    manufacturer_id = create_response.json()["id"]
    response = client.get(
        f"/suppliers/manufacturers/{manufacturer_id}/products"
    )
    assert response.status_code == 200
