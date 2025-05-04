# Mock database
import uuid
from typing import Any, Generator, List
from unittest import mock

import faker
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from db_dependency import get_db
from main import app as init_app
from rpc_clients.schemas import ManufacturerSchema, ProductSchema

SQLALCHEMY_DATABASE_URL = "sqlite://"
fake = faker.Faker()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture
def lite_engine() -> Any:
    return engine


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    yield init_app
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(app: FastAPI) -> Generator["TestingSessionLocal", Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at
    the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = TestingSessionLocal(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


@pytest.fixture()
def client(
    app: FastAPI, db_session: "TestingSessionLocal"
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
        # Set authorixation token
        yield client


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
                "manufacturer": ManufacturerSchema(
                    **{
                        "id": fake.uuid4(),
                        "manufacturer_name": fake.company(),
                    }
                ),
            }
        )
        for id in product_ids
    ]


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
