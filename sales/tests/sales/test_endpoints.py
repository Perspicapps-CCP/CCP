from typing import Callable, List
from unittest import mock
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from sales.models import Sale, SaleItem
from tests.conftest import generate_fake_sellers

fake = Faker()


@pytest.fixture
def seed_sales(db_session: Session) -> Callable[[int, int], List[Sale]]:
    """
    Seed the database with sales and their items for testing.

    Returns:
        Callable[[int, int], List[Sale]]:
          A function to seed sales with items.
    """

    def _seed_sales(count: int = 2, items_per_sale: int = 2) -> List[Sale]:
        sales = []
        for _ in range(count):
            sale = Sale(
                id=uuid4(),
                seller_id=uuid4(),
                order_number=fake.random_int(min=1000, max=9999),
                address_id=uuid4(),
                total_value=fake.pydecimal(
                    left_digits=5, right_digits=2, positive=True
                ),
                currency="USD",
                created_at=fake.date_time_this_year(),
                updated_at=fake.date_time_this_year(),
            )
            db_session.add(sale)
            db_session.commit()

            # Add items to the sale
            for _ in range(items_per_sale):
                item = SaleItem(
                    id=uuid4(),
                    sale_id=sale.id,
                    product_id=uuid4(),
                    quantity=fake.random_int(min=1, max=10),
                    unit_price=fake.pydecimal(
                        left_digits=3, right_digits=2, positive=True
                    ),
                    total_value=fake.pydecimal(
                        left_digits=4, right_digits=2, positive=True
                    ),
                    created_at=fake.date_time_this_year(),
                    updated_at=fake.date_time_this_year(),
                )
                db_session.add(item)

            sales.append(sale)
        db_session.commit()
        return sales

    return _seed_sales


def test_list_sales_with_data(client: TestClient, seed_sales):
    """
    Test the list sales endpoint when there are sales in the database.
    """
    sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales with 2 items each
    # Order by created_at to ensure the order is consistent
    sales.sort(key=lambda x: x.created_at, reverse=True)

    response = client.get("/api/v1/sales/sales/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    for i, sale in enumerate(sales):
        assert data[i]["id"] == str(sale.id)
        assert data[i]["order_number"] == sale.order_number
        assert data[i]["total_value"] == str(sale.total_value)
        assert data[i]["currency"] == sale.currency
        assert len(data[i]["items"]) == 2  # Verify items are included


def test_list_sales_empty_database(client: TestClient):
    """
    Test the list sales endpoint when the database is empty.
    """
    response = client.get("/api/v1/sales/sales/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


def test_filter_sales_by_order_number(client: TestClient, seed_sales):
    """
    Test filtering sales by order number.
    """
    sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales
    sale = sales[0]  # Use the first sale for filtering

    response = client.get(
        f"/api/v1/sales/sales/?order_number={sale.order_number}"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(sale.id)
    assert data[0]["order_number"] == sale.order_number
    assert data[0]["total_value"] == str(sale.total_value)
    assert data[0]["currency"] == sale.currency


def test_filter_sales_by_seller_id(client: TestClient, seed_sales):
    """
    Test filtering sales by seller ID.
    """
    sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales
    sale = sales[0]  # Use the first sale for filtering
    sale_last = sales[-1]  # Use the last sale for filtering

    response = client.get(
        f"/api/v1/sales/sales/?seller_id={sale.seller_id}&"
        f"seller_id={sale_last.seller_id}"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    for sale in [sale, sale_last]:
        assert any(
            item["id"] == str(sale.id)
            and item["seller"]["id"] == str(sale.seller_id)
            for item in data
        )


def test_filter_sales_by_date_range(client: TestClient, seed_sales):
    """
    Test filtering sales by start_date and end_date.
    """
    sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales
    start_date = sales[0].created_at.date()
    end_date = sales[-1].created_at.date()

    expected_sales = [
        sale
        for sale in sales
        if start_date <= sale.created_at.date() <= end_date
    ]
    expected_sales.sort(key=lambda x: x.created_at, reverse=True)

    response = client.get(
        f"/api/v1/sales/sales/?start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(
        expected_sales
    )  # All sales should fall within the range
    for sale, response_sale in zip(expected_sales, data):
        assert response_sale["id"] == str(sale.id)


@pytest.mark.skip_mock_users
def test_filter_sales_by_seller_name(client: TestClient, seed_sales):
    """
    Test filtering sales by seller name.
    """
    sells = seed_sales(3, items_per_sale=2)  # Seed 3 sales

    sellers = generate_fake_sellers([sale.seller_id for sale in sells])

    with mock.patch(
        "rpc_clients.users_client.UsersClient.get_sellers",
        return_value=sellers,
        autospec=True,
    ):
        response = client.get(
            f"/api/v1/sales/sales/?seller_name={sellers[0].full_name}"
        )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["seller"]["full_name"] == sellers[0].full_name


def test_get_sale_exists(client: TestClient, seed_sales):
    """
    Test retrieving a specific sale when it exists.
    """
    sales = seed_sales(1, items_per_sale=2)  # Seed 1 sale with 2 items
    sale = sales[0]

    response = client.get(f"/api/v1/sales/sales/{sale.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(sale.id)
    assert data["order_number"] == sale.order_number
    assert data["total_value"] == str(sale.total_value)
    assert data["currency"] == sale.currency
    assert len(data["items"]) == 2  # Verify items are included


def test_get_sale_not_found(client: TestClient):
    """
    Test retrieving a specific sale when it does not exist.
    """
    non_existent_sale_id = uuid4()

    response = client.get(f"/api/v1/sales/sales/{non_existent_sale_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found."
