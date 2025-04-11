from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from sales.models import Sale, SaleItem

fake = Faker()


@pytest.fixture
def seed_sales(db_session: Session):
    """
    Seed the database with sales and their items for testing.

    Returns:
        Callable[[int, int], List[Sale]]:
          A function to seed sales with items.
    """

    def _seed_sales(count: int = 2, items_per_sale: int = 2):
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
