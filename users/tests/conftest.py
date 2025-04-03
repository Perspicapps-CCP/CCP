# Mock database
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from db_dependency import get_db
from main import app as init_app

SQLALCHEMY_DATABASE_URL = "sqlite://"


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
