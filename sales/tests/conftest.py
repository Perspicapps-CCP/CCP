# Mock database
from typing import Any, Dict, Generator, List
from unittest import mock

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
from rpc_clients.schemas import ProductSchema, SellerSchema

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
    app: FastAPI, db_session: "Session"
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
    with TestClient(app) as client:
        # Set authorization token
        yield client


def generate_fake_sellers(seller_ids) -> List[Dict]:
    """
    Generate fake sellers for testing.
    """
    return [
        SellerSchema(
            **{
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
            }
        )
        for id in seller_ids
    ]


def generate_fake_products(product_ids) -> List[Dict]:
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

    def get_sellers(_self, seller_ids):
        return generate_fake_sellers(seller_ids)

    with mock.patch(
        "rpc_clients.users_client.UsersClient.get_sellers",
        side_effect=get_sellers,
        autospec=True,
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
        return generate_fake_products(product_ids)

    with mock.patch(
        "rpc_clients.suppliers_client.SuppliersClient.get_products",
        side_effect=get_products,
        autospec=True,
    ):
        yield
