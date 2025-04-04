# Mock database
from typing import Any, Generator
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from db_dependency import get_db
from main import app as init_app

SQLALCHEMY_DATABASE_URL = "sqlite://"

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
