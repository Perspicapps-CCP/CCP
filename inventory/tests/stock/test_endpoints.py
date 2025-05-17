import csv
import io
from unittest.mock import MagicMock
import uuid
import pytest
from faker import Faker
from fastapi.testclient import TestClient

from rpc_clients import schemas as rpc_schemas
from rpc_clients.suppliers_client import SuppliersClient
from stock.models import Stock
from warehouse.models import Warehouse

fake = Faker()
fake.seed_instance(0)


def mock_warehouse_db():
    return Warehouse(
        name="Test Warehouse",
        phone="1234567890",
        address_id=uuid.uuid4(),
    )


def mock_stock_db(dummy_warehouse):
    return Stock(
        warehouse_id=dummy_warehouse.id,
        product_id=uuid.uuid4(),
        quantity=fake.random_int(min=1, max=100),
    )


def mock_stock_dict(dummy_warehouse):
    return {
        "warehouse_id": str(dummy_warehouse.id),
        "product_id": str(fake.uuid4()),
        "quantity": fake.random_int(min=1, max=100),
    }


@pytest.fixture
def csv_dummy_file() -> bytes:
    """Helper para crear un archivo CSV de prueba"""
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(['product_code', 'quantity'])
    test_data = [
        [fake.uuid4(), fake.random_int(min=1, max=100)],
        [fake.uuid4(), fake.random_int(min=1, max=100)],
        [fake.uuid4(), fake.random_int(min=1, max=100)],
        [fake.uuid4(), fake.random_int(min=1, max=100)],
    ]

    for row in test_data:
        writer.writerow(row)
    csv_file.seek(0)
    return csv_file.read().encode('utf-8')


@pytest.fixture
def mock_suppliers_client():
    mock_client = MagicMock()
    mock_client.get_products.return_value = []
    return mock_client


def test_upload_inventory_success_create_stock(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)

    mock_suppliers_client.get_products.return_value = [
        {"id": dummy_stock["product_id"], "name": "Test Product"}
    ]
    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["warehouse_id"] == dummy_stock["warehouse_id"]


def test_upload_inventory_success_update_stock(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.flush()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_db(dummy_warehouse)
    db_session.add(dummy_stock)
    db_session.commit()
    db_session.refresh(dummy_stock)

    mock_suppliers_client.get_products.return_value = [
        {"id": dummy_stock.product_id, "name": "Test Product"}
    ]
    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    request = mock_stock_dict(dummy_warehouse)
    request["product_id"] = str(dummy_stock.product_id)

    # Act
    response = client.post(
        "/inventory/stock",
        json=request,
    )

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["warehouse_id"] == request["warehouse_id"]


def test_upload_inventory_failed_warehouse_not_exist(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)
    dummy_stock["warehouse_id"] = str(fake.uuid4())

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 404


def test_upload_inventory_failed_product_not_exist(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)
    dummy_stock["product_id"] = str(fake.uuid4())

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 404


def test_upload_inventory_failed_quantity_negative(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)
    dummy_stock["quantity"] = -1

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 400


def test_upload_inventory_failed_warehouse_invalid_format(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)
    dummy_stock["warehouse_id"] = fake.iana_id()

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 422


def test_upload_inventory_failed_product_invalid_format(
    client: TestClient, db_session, mock_suppliers_client
) -> None:
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_dict(dummy_warehouse)
    dummy_stock["product_id"] = fake.iana_id()

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock",
        json=dummy_stock,
    )

    # Assert
    assert response.status_code == 422


def test_upload_inventory_csv_success(
    client: TestClient,
    csv_dummy_file: bytes,
    db_session,
    mock_suppliers_client,
) -> None:
    """
    Test uploading a CSV file with inventory data.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    mock_suppliers_client.get_products.return_value = [
        {"id": str(fake.uuid4), "name": "Test Product"}
    ]
    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    files = {
        "inventory_upload": (
            "test.csv",
            csv_dummy_file,
            "application/octet-stream",
        )
    }
    data = {"warehouse_id": str(dummy_warehouse.id)}

    # Act
    response = client.post(
        "/inventory/stock/csv",
        files=files,
        data=data,
    )

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["warehouse_id"] == str(dummy_warehouse.id)


def test_upload_inventory_csv_failed_warehouse_invalid_format(
    client: TestClient,
    csv_dummy_file: bytes,
    mock_suppliers_client,
) -> None:
    """
    Test uploading a CSV file with inventory data.
    """
    # Arrange
    files = {
        "inventory_upload": (
            "test.xls",
            csv_dummy_file,
            "application/octet-stream",
        )
    }
    data = {"warehouse_id": fake.iana_id()}

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock/csv",
        files=files,
        data=data,
    )

    # Assert
    assert response.status_code == 422


def test_upload_inventory_csv_failed_warehouse_not_exist(
    client: TestClient,
    csv_dummy_file: bytes,
    mock_suppliers_client,
) -> None:
    """
    Test uploading a CSV file with unknow warehouse.
    """
    # Arrange
    files = {
        "inventory_upload": (
            "test.csv",
            csv_dummy_file,
            "application/octet-stream",
        )
    }
    data = {"warehouse_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock/csv",
        files=files,
        data=data,
    )

    # Assert
    assert response.status_code == 404


def test_upload_inventory_csv_failed_invalid_file_format(
    client: TestClient,
    csv_dummy_file: bytes,
    db_session,
    mock_suppliers_client,
) -> None:
    """
    Test uploading a CSV file with invalid file format.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    files = {
        "inventory_upload": (
            "test.xls",
            csv_dummy_file,
            "application/octet-stream",
        )
    }
    data = {"warehouse_id": str(dummy_warehouse.id)}

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.post(
        "/inventory/stock/csv",
        files=files,
        data=data,
    )

    # Assert
    assert response.status_code == 400


def test_upload_inventory_csv_failed_product_not_exist(
    client: TestClient,
    csv_dummy_file: bytes,
    db_session,
    mock_suppliers_client,
) -> None:
    """
    Test uploading a CSV file with inventory data.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    files = {
        "inventory_upload": (
            "test.csv",
            csv_dummy_file,
            "application/octet-stream",
        )
    }
    data = {"warehouse_id": str(dummy_warehouse.id)}

    # Act
    response = client.post(
        "/inventory/stock/csv",
        files=files,
        data=data,
    )

    # Assert
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["warehouse_id"] == str(dummy_warehouse.id)
    assert response_data["failed_records"] > 0


def test_get_stock_success_with_filters(
    client: TestClient, db_session
) -> None:
    """
    Test getting stock with valid filters.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.flush()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_db(dummy_warehouse)
    db_session.add(dummy_stock)
    db_session.commit()
    db_session.refresh(dummy_stock)

    warehouse_param = {"warehouse": str(dummy_warehouse.id)}
    product_param = {"product": str(dummy_stock.product_id)}

    # Act
    response_warehouse_filter = client.get(
        "/inventory/stock",
        params=warehouse_param,
    )

    response_product_filter = client.get(
        "/inventory/stock",
        params=product_param,
    )

    # Assert
    assert response_warehouse_filter.status_code == 200
    assert isinstance(response_warehouse_filter.json(), list)
    assert len(response_warehouse_filter.json()) > 0

    assert response_product_filter.status_code == 200
    assert isinstance(response_product_filter.json(), list)
    assert len(response_product_filter.json()) > 0


def test_get_stock_success_without_filters(
    client: TestClient, db_session
) -> None:
    """
    Test getting stock without filters.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.commit()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_db(dummy_warehouse)
    db_session.add(dummy_stock)
    db_session.commit()
    db_session.refresh(dummy_stock)

    # Act
    response = client.get("/inventory/stock")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_stock_failed_with_invalid_warehouse_format(
    client: TestClient,
) -> None:
    """
    Test getting stock with invalid warehouse format.
    """
    # Arrange
    params = {"warehouse": fake.iana_id()}

    # Act
    response = client.get(
        "/inventory/stock",
        params=params,
    )

    # Assert
    assert response.status_code == 422


def test_get_stock_failed_with_invalid_product_format(
    client: TestClient,
) -> None:
    """
    Test getting stock with invalid product format.
    """
    # Arrange
    params = {"product": fake.iana_id()}

    # Act
    response = client.get(
        "/inventory/stock",
        params=params,
    )

    # Assert
    assert response.status_code == 422


def test_get_aggregated_stock_success(
    client: TestClient,
    db_session,
    mock_suppliers_client,
) -> None:
    """
    Test getting aggregated stock.
    """
    # Arrange
    dummy_warehouse = mock_warehouse_db()
    db_session.add(dummy_warehouse)
    db_session.flush()
    db_session.refresh(dummy_warehouse)

    dummy_stock = mock_stock_db(dummy_warehouse)
    db_session.add(dummy_stock)
    db_session.commit()
    db_session.refresh(dummy_stock)

    dummy_product = rpc_schemas.ProductSchema(
        id=dummy_stock.product_id,
        name="Unknown Product",
        product_code="N/A",
        manufacturer=rpc_schemas.ManufacturerSchema(
            id=uuid.UUID(int=0), manufacturer_name="Unknown"
        ),
        price=0.0,
        images=["https://example.com/default_image.png"],
    )

    mock_suppliers_client.get_products.return_value = [dummy_product]
    client.app.dependency_overrides[SuppliersClient] = (
        lambda: mock_suppliers_client
    )

    # Act
    response = client.get("/inventory/stock/catalog")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "quantity" in response.json()[0]
    assert "product_id" in response.json()[0]
