from uuid import UUID, uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from plans.models import SalesPlan, SellerInPlan

fake = Faker()


@pytest.fixture
def valid_payload():
    """
    Returns a valid payload for creating a sales plan.
    """
    return {
        "product_id": str(uuid4()),
        "goal": 1000,
        "start_date": "2025-03-01",
        "end_date": "2025-03-31",
        "seller_ids": [str(uuid4()), str(uuid4())],
    }


def test_missing_fields(client: TestClient, valid_payload):
    """
    Test missing fields in the payload.
    """
    payload = valid_payload.copy()
    del payload["product_id"]  # Remove a required field
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "product_id" in response.json()["detail"][0]["loc"]


def test_invalid_dates(client: TestClient, valid_payload):
    """
    Test invalid date formats.
    """
    payload = valid_payload.copy()
    payload["start_date"] = "invalid-date"
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "start_date" in response.json()["detail"][0]["loc"]


def test_start_date_after_end_date(client: TestClient, valid_payload):
    """
    Test when the start date is after the end date.
    """
    payload = valid_payload.copy()
    payload["start_date"] = "2025-04-01"
    payload["end_date"] = "2025-03-31"
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "end_date" in response.json()["detail"][0]["loc"]


def test_invalid_product_id(client: TestClient, valid_payload, monkeypatch):
    """
    Test invalid product ID.
    """

    def mock_get_products(self, product_ids):
        return []  # Simulate no products found

    monkeypatch.setattr(
        "rpc_clients.suppliers_client.SuppliersClient.get_products",
        mock_get_products,
    )
    payload = valid_payload.copy()
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "product_id" in response.json()["detail"][0]["loc"]


def test_invalid_seller_ids(client: TestClient, valid_payload, monkeypatch):
    """
    Test invalid seller IDs.
    """

    def mock_get_sellers(self, seller_ids):
        return []  # Simulate no sellers found

    monkeypatch.setattr(
        "rpc_clients.users_client.UsersClient.get_sellers",
        mock_get_sellers,
    )

    payload = valid_payload.copy()
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "seller_ids" in response.json()["detail"][0]["loc"]


def test_invalid_goal(client: TestClient, valid_payload):
    """
    Test invalid goal (e.g., less than 1).
    """
    payload = valid_payload.copy()
    payload["goal"] = 0  # Invalid goal
    response = client.post("/api/v1/sales/plans", json=payload)
    assert response.status_code == 422
    assert "goal" in response.json()["detail"][0]["loc"]


def test_successful_creation(
    client: TestClient, db_session: Session, valid_payload
):
    """
    Test successful creation of a sales plan.
    """
    response = client.post("/api/v1/sales/plans", json=valid_payload)
    assert response.status_code == 201

    # Verify the response contains the correct data
    response_data = response.json()
    assert response_data["product"]["id"] == valid_payload["product_id"]
    assert response_data["goal"] == valid_payload["goal"]
    assert response_data["start_date"] == valid_payload["start_date"]
    assert response_data["end_date"] == valid_payload["end_date"]
    assert len(response_data["sellers"]) == len(valid_payload["seller_ids"])

    # Verify the sales plan is inserted into the database
    db_plan = (
        db_session.query(SalesPlan)
        .filter_by(id=UUID(response_data["id"]))
        .first()
    )
    assert db_plan is not None
    assert db_plan.product_id == UUID(valid_payload["product_id"])
    assert db_plan.goal == valid_payload["goal"]

    # Verify the sellers are linked to the plan
    db_sellers = (
        db_session.query(SellerInPlan).filter_by(plan_id=db_plan.id).all()
    )
    assert len(db_sellers) == len(valid_payload["seller_ids"])
    db_seller_ids = [str(seller.seller_id) for seller in db_sellers]
    assert set(db_seller_ids) == set(valid_payload["seller_ids"])
