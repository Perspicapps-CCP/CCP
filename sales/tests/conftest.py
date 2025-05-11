# Mock database
import uuid
from typing import Any, Generator, List
from unittest import mock
from unittest.mock import MagicMock

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from db_dependency import get_db
from main import app as init_app
from rpc_clients.schemas import ProductSchema, UserAuthSchema, UserSchema
from storage_dependency import get_storage_bucket

SQLALCHEMY_DATABASE_URL = "sqlite://"


fake = Faker()


@pytest.fixture(scope="function")
def lite_engine() -> Engine:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    return engine


@pytest.fixture(autouse=True)
def app(lite_engine: Engine) -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(lite_engine)  # Create the tables.
    yield init_app
    Base.metadata.drop_all(lite_engine)


@pytest.fixture
def mock_storage_bucket() -> Generator[MagicMock, Any, None]:
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    yield mock_bucket


@pytest.fixture
def db_session(
    app: FastAPI, lite_engine: Engine
) -> Generator["Session", Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at
    the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = lite_engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=lite_engine
    )
    session = TestingSessionLocal(bind=connection)
    try:
        yield session  # use the session in tests.
    finally:
        session.close()
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        transaction.rollback()
        # return connection to the Engine
        connection.close()


@pytest.fixture()
def client(
    app: FastAPI, mock_storage_bucket, db_session: "Session"
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session`
    fixture to override the `get_db` dependency that is injected
    into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_storage_bucket] = lambda: mock_storage_bucket
    with TestClient(app) as client:
        # Set authorization token
        yield client


def generate_fake_sellers(
    seller_ids, with_address: bool = False
) -> List[UserSchema]:
    """
    Generate fake sellers for testing.
    """
    return [
        UserSchema.model_validate(
            {
                "id": id,
                "full_name": fake.name(),
                "email": fake.email(),
                "username": fake.user_name(),
                "phone": fake.phone_number(),
                "id_type": fake.random_element(elements=("ID", "Passport")),
                "identification": str(
                    fake.random_int(min=100000, max=999999)
                ),
                "created_at": fake.date_time().isoformat(),
                "updated_at": fake.date_time().isoformat(),
                "address": (
                    {
                        "id": str(fake.uuid4()),
                        "line": fake.street_address(),
                        "neighborhood": fake.city(),
                        "city": fake.city(),
                        "state": fake.state(),
                        "country": fake.country(),
                        "latitude": float(fake.latitude()),
                        "longitude": float(fake.longitude()),
                    }
                    if with_address
                    else None
                ),
            }
        )
        for id in seller_ids
    ]


def generate_fake_products(product_ids) -> List[ProductSchema]:
    """
    Generate fake products for testing.
    """
    return [
        ProductSchema(
            **{
                "id": id,
                "product_code": str(fake.random_int(min=1000, max=9999)),
                "name": fake.word(),
                "price": fake.random_number(digits=5),
                "images": [fake.image_url() for _ in range(3)],
            }
        )
        for id in product_ids
    ]


@pytest.fixture(autouse=True)
def mock_users_rpc_client(request):
    """
    Mock the UsersClient to avoid actual RPC calls.
    """
    if request.node.get_closest_marker("skip_mock_users"):
        yield  # Skip the fixture
        return

    def get_sellers(seller_ids=None):
        """
        Mock the get_sellers method to return fake sellers.
        """
        if seller_ids is None:
            seller_ids = [uuid.uuid4() for _ in range(5)]
        return generate_fake_sellers(seller_ids)

    def get_clients(client_ids=None):
        """
        Mock the get_clients method to return fake clients.
        """
        if client_ids is None:
            client_ids = [uuid.uuid4() for _ in range(5)]
        return generate_fake_sellers(client_ids, with_address=True)

    def auth_user(bearer: str):
        if bearer == "invalid_token":
            return None

        auth_user = generate_fake_sellers(
            [uuid.UUID(bearer)], with_address=True
        )[0]
        is_client = bool(
            request.node.get_closest_marker("mock_auth_as_client")
        )
        return UserAuthSchema(
            **auth_user.model_dump(),
            is_active=True,
            is_seller=not is_client,
            is_client=is_client,
        )

    with mock.patch.multiple(
        "rpc_clients.users_client.UsersClient",
        get_sellers=mock.Mock(side_effect=get_sellers),
        get_clients=mock.Mock(side_effect=get_clients),
        auth_user=mock.Mock(side_effect=auth_user),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_suppliers_rpc_client(request):
    """
    Mock the SuppliersClient to avoid actual RPC calls.
    """
    if request.node.get_closest_marker("skip_mock_suppliers"):
        yield  # Skip the fixture
        return

    def get_products(_self, product_ids):
        if product_ids is None:
            product_ids = [uuid.uuid4() for _ in range(5)]
        return generate_fake_products(product_ids)

    with mock.patch(
        "rpc_clients.suppliers_client.SuppliersClient.get_products",
        side_effect=get_products,
        autospec=True,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_inventory_inventory_client(request):
    """
    Mock the InventoryClient to avoid actual RPC calls.
    """
    if request.node.get_closest_marker("skip_mock_inventory_client"):
        return

    with mock.patch(
        "rpc_clients.inventory_client.InventoryClient",
        autospec=True,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_logistic_client(request):
    """
    Mock the LogisticClient to avoid actual RPC calls.
    """

    if request.node.get_closest_marker("skip_mock_logistic_client"):
        return

    with mock.patch(
        "rpc_clients.logistic_client.LogisticClient.get_deliveries",
        autospec=True,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_rabbitmq_client(request):
    """
    Mock the RabbitMQ client (pika) to avoid actual RabbitMQ calls.
    """
    if request.node.get_closest_marker("skip_mock_rabbitmq"):
        yield  # Skip the fixture
        return

    # Mock the pika connection and channel
    mock_connection = mock.MagicMock()
    mock_channel = mock.MagicMock()

    # Mock pika.BlockingConnection to return the mock connection
    with mock.patch("pika.BlockingConnection", return_value=mock_connection):
        # Mock the connection.channel() to return the mock channel
        mock_connection.channel.return_value = mock_channel
        yield mock_channel
