import copy
import csv
from typing import Callable, Dict, List, Optional
from unittest import mock
from uuid import UUID

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from rpc_clients.schemas import UserAuthSchema
from sales.models import Sale, SaleItem
from sellers.models import ClientForSeller
from tests.conftest import generate_fake_sellers

fake = Faker()


def create_sales(
    db_session: Session,
    count: int = 2,
    items_per_sale: int = 2,
    sale_kwargs: Dict = None,
) -> List[Sale]:
    sales = []
    for _ in range(count):
        sale_body = {
            "id": fake.uuid4(cast_to=None),
            "seller_id": fake.uuid4(cast_to=None),
            "client_id": fake.uuid4(cast_to=None),
            "order_number": fake.random_int(min=1000, max=9999),
            "address_id": fake.uuid4(cast_to=None),
            "total_value": fake.pydecimal(
                left_digits=5, right_digits=2, positive=True
            ),
            "currency": "USD",
            "created_at": fake.date_time_this_year(),
            "updated_at": fake.date_time_this_year(),
            **(sale_kwargs or {}),
        }
        sale = Sale(**sale_body)
        db_session.add(sale)
        db_session.commit()

        # Add items to the sale
        for _ in range(items_per_sale):
            item = SaleItem(
                id=fake.uuid4(cast_to=None),
                sale_id=sale.id,
                product_id=fake.uuid4(cast_to=None),
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
    sales.sort(key=lambda x: x.created_at, reverse=True)
    return sales


@pytest.fixture
def seed_sales(db_session: Session) -> Callable[[int, int], List[Sale]]:
    """
    Seed the database with sales and their items for testing.

    Returns:
        Callable[[int, int], List[Sale]]:
          A function to seed sales with items.
    """

    def _seed_sales(
        count: int = 2,
        items_per_sale: int = 2,
        sale_kwargs: Optional[Dict] = None,
    ) -> List[Sale]:
        return create_sales(
            db_session,
            count=count,
            items_per_sale=items_per_sale,
            sale_kwargs=sale_kwargs,
        )

    return _seed_sales


class MixinListSales:

    @pytest.fixture
    def seed_sales(
        self, db_session: Session, auth_user_uuid: UUID
    ) -> Callable[[int, int], List[Sale]]:
        """
        Fixture to seed sales in the database for testing.
        """
        # Some sales that do no belong to the user

        def _seed_sales(
            count: int = 2, items_per_sale: int = 2, sale_kwargs: Dict = None
        ) -> List[Sale]:
            create_sales(
                db_session,
                count=count,
                items_per_sale=items_per_sale,
            )
            # Sales that belong to the user
            return create_sales(
                db_session,
                count=count,
                items_per_sale=items_per_sale,
                sale_kwargs={
                    "seller_id": auth_user_uuid,
                    **(sale_kwargs or {}),
                },
            )

        return _seed_sales

    @pytest.fixture
    def auth_client(
        self, client: TestClient, auth_user_uuid: UUID
    ) -> TestClient:
        """
        Fixture to provide an authenticated client for testing.
        """
        client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})
        return client

    def test_list_sales_with_data(self, auth_client: TestClient, seed_sales):
        """
        Test the list sales endpoint when there are sales in the database.
        """
        sales = seed_sales(
            3, items_per_sale=2
        )  # Seed 3 sales with 2 items each
        response = auth_client.get("/api/v1/sales/sales/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3
        for i, sale in enumerate(sales):
            assert data[i]["id"] == str(sale.id)
            assert data[i]["order_number"] == sale.order_number
            assert data[i]["total_value"] == str(sale.total_value)
            assert data[i]["currency"] == sale.currency
            assert len(data[i]["items"]) == 2  # Verify items are included

    def test_list_sales_empty_database(self, auth_client: TestClient):
        """
        Test the list sales endpoint when the database is empty.
        """
        response = auth_client.get("/api/v1/sales/sales/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 0

    def test_filter_sales_by_order_number(
        self, auth_client: TestClient, seed_sales
    ):
        """
        Test filtering sales by order number.
        """
        sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales
        sale = sales[0]  # Use the first sale for filtering

        response = auth_client.get(
            f"/api/v1/sales/sales/?order_number={sale.order_number}"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(sale.id)
        assert data[0]["order_number"] == sale.order_number
        assert data[0]["total_value"] == str(sale.total_value)
        assert data[0]["currency"] == sale.currency

    def test_filter_sales_by_seller_id(
        self,
        auth_client: TestClient,
        seed_sales: Callable,
        request: pytest.FixtureRequest,
    ):
        """
        Test filtering sales by seller ID.
        """
        sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales
        sale = sales[0]  # Use the first sale for filtering
        sale_last = sales[-1]  # Use the last sale for filtering

        is_client = bool(
            request.node.get_closest_marker("mock_auth_as_client")
        )

        response = auth_client.get(
            f"/api/v1/sales/sales/?seller_id={sale.seller_id}&"
            f"seller_id={sale_last.seller_id}"
        )
        assert response.status_code == 200

        data = response.json()
        expected = [sale, sale_last]
        if not is_client:
            expected = sales
        assert len(expected) == len(data)
        for sale in expected:
            assert any(
                item["id"] == str(sale.id)
                and item["seller"]["id"] == str(sale.seller_id)
                for item in data
            )

    def test_filter_sales_by_date_range(
        self, auth_client: TestClient, seed_sales
    ):
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

        response = auth_client.get(
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
    def test_filter_sales_by_seller_name(
        self,
        auth_client: TestClient,
        auth_user_uuid: UUID,
        seed_sales: Callable,
        request: pytest.FixtureRequest,
    ):
        """
        Test filtering sales by seller name.
        """
        seed_sales(
            3,
            items_per_sale=2,
            sale_kwargs={"seller_id": fake.uuid4(cast_to=None)},
        )
        sells = seed_sales(3, items_per_sale=2)  # Seed 3 sales

        sellers = generate_fake_sellers({sale.seller_id for sale in sells})
        buyers = generate_fake_sellers(
            [sale.client_id for sale in sells], with_address=True
        )
        is_client = bool(
            request.node.get_closest_marker("mock_auth_as_client")
        )
        with mock.patch.multiple(
            "rpc_clients.users_client.UsersClient",
            get_sellers=mock.Mock(return_value=sellers),
            get_clients=mock.Mock(return_value=buyers),
            auth_user=mock.Mock(
                return_value=UserAuthSchema(
                    **(
                        generate_fake_sellers(
                            [auth_user_uuid], with_address=True
                        )[0].model_dump()
                    ),
                    is_active=True,
                    is_seller=not is_client,
                    is_client=is_client,
                )
            ),
        ):
            response = auth_client.get(
                f"/api/v1/sales/sales/?seller_name={sellers[0].full_name}"
            )
        assert response.status_code == 200

        data = response.json()
        if is_client:
            assert len(data) == 1
            assert data[0]["seller"]["full_name"] == sellers[0].full_name
        else:
            assert len(data) == 3


class TestGetSalesAsSeller(MixinListSales):
    @pytest.fixture
    def auth_user_uuid(self):
        return fake.uuid4(cast_to=None)


class TestGetSalesAsClient(MixinListSales):
    @pytest.mark.mock_auth_as_client
    @pytest.fixture(autouse=True)
    def auth_user_uuid(self):
        return fake.uuid4(cast_to=None)


def test_get_sale_exists(client: TestClient, seed_sales):
    """
    Test retrieving a specific sale when it exists.
    """
    auth_user_uuid = fake.uuid4(cast_to=None)
    client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})

    sales = seed_sales(
        1,
        items_per_sale=2,
        sale_kwargs={"seller_id": auth_user_uuid},
    )  # Seed 1 sale with 2 items
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
    non_existent_sale_id = fake.uuid4(cast_to=None)
    auth_user_uuid = fake.uuid4(cast_to=None)
    client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})
    response = client.get(f"/api/v1/sales/sales/{non_existent_sale_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found."


@pytest.mark.mock_auth_as_client
def test_get_sale_not_found_as_client(client: TestClient, seed_sales):
    """
    Test retrieving a specific sale when it does not exist.
    """
    auth_user_uuid = fake.uuid4(cast_to=None)
    client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})
    sales = seed_sales(
        1,
        items_per_sale=2,
    )  # Seed 1 sale with 2 items
    response = client.get(f"/api/v1/sales/sales/{sales[0].id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found."


def test_get_sale_not_found_as_sellers(client: TestClient, seed_sales):
    """
    Test retrieving a specific sale when it does not exist.
    """
    auth_user_uuid = fake.uuid4(cast_to=None)
    client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})
    sales = seed_sales(
        1,
        items_per_sale=2,
    )  # Seed 1 sale with 2 items
    response = client.get(f"/api/v1/sales/sales/{sales[0].id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found."


def test_export_sales_as_csv(client: TestClient, seed_sales):
    """
    Test exporting sales as a CSV file.
    """
    sales = seed_sales(3, items_per_sale=2)  # Seed 3 sales

    response = client.get("/api/v1/sales/sales/export/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"].startswith(
        "attachment; filename="
    )
    assert response.headers["Content-Disposition"].endswith("_sales.csv")
    # Verify the CSV content
    csv_content = response.content.decode("utf-8")

    # Parse as CSV
    csv_reader = csv.reader(csv_content.splitlines())
    header = next(csv_reader)
    assert header == [
        "Sale ID",
        "Order Number",
        "Seller ID",
        "Seller Name",
        "Total Value",
        "Currency",
        "Sale At",
    ]
    for sale in sales:
        row = next(csv_reader)
        assert row[0] == str(sale.id)
        assert row[1] == str(sale.order_number)
        assert row[2] == str(sale.seller_id)
        assert row[4] == str(sale.total_value)
        assert row[5] == sale.currency
        assert row[6] == sale.created_at.isoformat()

    # Ensure no extra rows in the CSV
    with pytest.raises(StopIteration):
        next(csv_reader)


def test_export_sales_as_csv_with_filters(client: TestClient, seed_sales):
    """
    Test exporting sales as a CSV file with seller and date filters.
    """
    # Seed 5 sales with 2 items each
    sales = seed_sales(5, items_per_sale=2)

    # Use the first sale's seller_id and date range for filtering
    seller_id = sales[0].seller_id
    start_date = sales[0].created_at.date()
    end_date = sales[-1].created_at.date()

    # Filtered sales
    filtered_sales = [
        sale
        for sale in sales
        if sale.seller_id == seller_id
        and start_date <= sale.created_at.date() <= end_date
    ]

    response = client.get(
        f"/api/v1/sales/sales/export/?seller_id={seller_id}&"
        f"start_date={start_date}&end_date={end_date}"
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"].startswith(
        "attachment; filename="
    )
    assert response.headers["Content-Disposition"].endswith("_sales.csv")

    # Verify the CSV content
    csv_content = response.content.decode("utf-8")

    # Parse as CSV
    csv_reader = csv.reader(csv_content.splitlines())
    header = next(csv_reader)
    assert header == [
        "Sale ID",
        "Order Number",
        "Seller ID",
        "Seller Name",
        "Total Value",
        "Currency",
        "Sale At",
    ]

    # Verify filtered sales in the CSV
    for sale in filtered_sales:
        row = next(csv_reader)
        assert row[0] == str(sale.id)
        assert row[1] == str(sale.order_number)
        assert row[2] == str(sale.seller_id)
        assert row[4] == str(sale.total_value)
        assert row[5] == sale.currency
        assert row[6] == sale.created_at.isoformat()

    # Ensure no extra rows in the CSV
    with pytest.raises(StopIteration):
        next(csv_reader)


class CreateSaleMixin:
    @pytest.fixture
    def auth_client(
        self, client: TestClient, auth_user_uuid: UUID
    ) -> TestClient:
        """
        Fixture to provide an authenticated client for testing.
        """
        client.headers.update({"Authorization": f"Bearer {auth_user_uuid}"})
        return client

    @pytest.fixture
    def is_user_seller(self, request) -> bool:
        return not bool(
            request.node.get_closest_marker("mock_auth_as_client")
        )

    @pytest.fixture
    def existing_sales(self, db_session: Session):
        """
        Fixture to create existing sales for testing.
        """
        create_sales(db_session)

    @pytest.fixture
    def base_payload(self) -> Dict:
        return {
            "items": [
                {
                    "product_id": fake.uuid4(),
                    "quantity": fake.random_int(min=1, max=10),
                }
                for _ in range(4)
            ]
        }

    @pytest.fixture
    def payload(self, base_payload: Dict) -> Dict:
        return base_payload

    def test_not_authenticated(self, client: TestClient):
        """
        Test creating a sale when not authenticated.
        """
        response = client.post("/api/v1/sales/sales/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.usefixtures("existing_sales")
    def test_create_sale(
        self,
        db_session: Session,
        auth_client: TestClient,
        payload: Dict,
        is_user_seller: bool,
        auth_user_uuid: UUID,
    ):
        """
        Test creating a sale with valid data.
        """
        qs = db_session.query(Sale)
        assert qs.count() == 2
        if is_user_seller:
            qs = qs.filter(Sale.seller_id == auth_user_uuid)
        else:
            qs = qs.filter(Sale.client_id == auth_user_uuid)
        assert qs.count() == 0
        response = auth_client.post(
            "/api/v1/sales/sales/",
            json=payload,
        )
        assert response.status_code == 201, response.json()
        assert response.json()["id"] is not None
        assert qs.count() == 1
        sale = qs.filter(Sale.id == UUID(response.json()["id"])).first()
        assert sale is not None
        assert len(sale.items) == len(payload["items"])

    @pytest.mark.skip_mock_inventory_client
    def test_not_enough_inventory(
        self, auth_client: TestClient, payload: Dict, db_session: Session
    ):

        def reserve_stock(
            _self,
            payload: Dict,
        ) -> Dict:
            return {
                "error": "Not enough stock",
            }

        with mock.patch(
            "rpc_clients.inventory_client.InventoryClient.reserve_stock",
            side_effect=reserve_stock,
            autospec=True,
        ):
            response = auth_client.post(
                "/api/v1/sales/sales/",
                json=payload,
            )
        assert response.status_code == 422
        assert response.json()["detail"] == {
            "error": "Not enough stock",
        }
        assert db_session.query(Sale).count() == 0


class TestCreaeSaleAsSeller(CreateSaleMixin):

    @pytest.fixture
    def auth_user_uuid(self):

        return fake.uuid4(cast_to=None)

    @pytest.fixture
    def client_uuid(self, db_session: Session, auth_user_uuid: UUID) -> UUID:
        client_id = fake.uuid4(cast_to=None)
        relation = ClientForSeller(
            client_id=client_id, seller_id=auth_user_uuid
        )
        db_session.add(relation)
        db_session.commit()
        return client_id

    @pytest.fixture
    def payload(self, base_payload: Dict, client_uuid: UUID) -> Dict:
        payload = copy.deepcopy(base_payload)
        payload["client_id"] = str(client_uuid)
        return payload


class TestCreateSaleAsClient(CreateSaleMixin):
    @pytest.fixture(autouse=True)
    def setup(
        self,
        mock_users_client: Callable,
    ):
        """
        Fixture to set up the test environment.
        """
        # Create a client for the seller
        with mock_users_client(as_seller=False):
            yield

    @pytest.fixture
    def auth_user_uuid(self):
        return fake.uuid4(cast_to=None)

    @pytest.fixture
    def is_user_seller(self) -> bool:
        return False
