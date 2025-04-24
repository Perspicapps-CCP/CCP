import json
import uuid
from typing import List
from unittest import mock

import pytest
from faker import Faker
from sqlalchemy.orm import Session
from users.auth import create_access_token
from users.consumers import (
    AuthUserConsumer,
    GetClientsConsumer,
    GetSellersConsumer,
)
from users.models import Address, RoleEnum, User

fake = Faker()


def generate_users_with_role(total: int, role: RoleEnum) -> List[User]:
    """
    Generate a list of users with the specified role.
    """
    return [
        User(
            id=uuid.uuid4(),
            username=fake.user_name(),
            email=fake.email(),
            hashed_password=fake.password(length=12),
            full_name=fake.name(),
            phone=fake.phone_number(),
            role=role,
            is_active=True,
        )
        for _ in range(total)
    ]


@pytest.fixture
def sellers_in_db(db_session: Session) -> List[User]:
    """
    Fixture to create sellers in the database for testing.
    """
    sellers = generate_users_with_role(5, RoleEnum.SELLER)
    db_session.add_all(sellers)
    db_session.commit()
    return sellers


@pytest.fixture
def clients_in_db(db_session: Session) -> List[User]:
    """
    Fixture to create clients in the database for testing.
    """
    clients = generate_users_with_role(5, RoleEnum.CLIENT)
    db_session.add_all(clients)
    db_session.commit()
    # Add address to clients
    for client in clients:
        address = Address(
            id=uuid.uuid4(),
            user_id=client.id,
            line=fake.street_address(),
            neighborhood=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
        )
        db_session.add(address)
    db_session.commit()
    return clients


class TestGetSellersConsumer:
    """
    Test suite for the GetSellersConsumer class.
    """

    def test_invalid_payload(self):
        """
        Test GetSellersConsumer with an invalid payload.
        """
        consumer = GetSellersConsumer()
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(
            response["error"], list
        )  # Validation errors are returned as a list
        assert response["error"][0]["loc"] == ("seller_ids",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self, db_session: Session, sellers_in_db: list[User]
    ):
        """
        Test GetSellersConsumer with a valid payload and verify the data.
        """
        consumer = GetSellersConsumer()
        select_sellers = sellers_in_db[:2]  # Select first two sellers

        # Prepare a valid payload with seller IDs
        seller_ids = [str(seller.id) for seller in select_sellers]
        valid_payload = {"seller_ids": seller_ids}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            sellers_data = consumer.process_payload(valid_payload)
            sellers_data = json.loads(sellers_data)

        assert "sellers" in sellers_data
        sellers_data = sellers_data["sellers"]

        assert len(sellers_data) == len(select_sellers)
        for seller, seller_data in zip(select_sellers, sellers_data):
            assert str(seller.id) == seller_data["id"]
            assert seller.username == seller_data["username"]
            assert seller.email == seller_data["email"]
            assert seller.full_name == seller_data["full_name"]
            assert seller.phone == seller_data["phone"]
            assert seller.role == seller_data["role"]

    def test_list_missing_sellers(self, db_session: Session):
        """
        Test GetsellersConsumer with a valid payload and verify the data.
        """
        consumer = GetSellersConsumer()
        valid_payload = {
            "seller_ids": [
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                str(uuid.uuid4()),
            ]
        }
        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            sellers_data = consumer.process_payload(valid_payload)
            sellers_data = json.loads(sellers_data)

        assert "sellers" in sellers_data
        assert len(sellers_data["sellers"]) == 0

    @pytest.mark.usefixtures("sellers_in_db")
    def test_empty_sellers(self, db_session: Session):
        """
        Test GetsellersConsumer with an empty list of product IDs.
        """
        consumer = GetSellersConsumer()
        valid_payload = {"seller_ids": []}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            sellers_data = consumer.process_payload(valid_payload)
            sellers_data = json.loads(sellers_data)

        assert "sellers" in sellers_data
        assert len(sellers_data["sellers"]) == 0

    def test_get_all_sellers(
        self, db_session: Session, sellers_in_db: list[User]
    ):
        """
        Test GetSellersConsumer with a valid payload and verify the data.
        """
        consumer = GetSellersConsumer()
        valid_payload = {"seller_ids": None}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            sellers_data = consumer.process_payload(valid_payload)
            sellers_data = json.loads(sellers_data)

        assert "sellers" in sellers_data
        assert len(sellers_data["sellers"]) == len(sellers_in_db)
        assert {str(seller.id) for seller in sellers_in_db} == {
            seller["id"] for seller in sellers_data["sellers"]
        }


class TestGetClientsConsumer:
    """
    Test suite for the GetClientsConsumer class.
    """

    def test_invalid_payload(self):
        """
        Test GetClientsConsumer with an invalid payload.
        """
        consumer = GetClientsConsumer()
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(
            response["error"], list
        )  # Validation errors are returned as a list
        assert response["error"][0]["loc"] == ("client_ids",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self, db_session: Session, clients_in_db: list[User]
    ):
        """
        Test GetClientsConsumer with a valid payload and verify the data.
        """
        consumer = GetClientsConsumer()
        select_clients = clients_in_db[:2]  # Select first two clients

        # Prepare a valid payload with client IDs
        client_ids = [str(client.id) for client in select_clients]
        valid_payload = {"client_ids": client_ids}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            clients_data = consumer.process_payload(valid_payload)
            clients_data = json.loads(clients_data)
        assert "clients" in clients_data
        clients_data = clients_data["clients"]
        assert len(clients_data) == len(select_clients)
        for client, client_data in zip(select_clients, clients_data):
            assert str(client.id) == client_data["id"]
            assert client.username == client_data["username"]
            assert client.email == client_data["email"]
            assert client.full_name == client_data["full_name"]
            assert client.phone == client_data["phone"]
            assert client.role == client_data["role"]
            assert str(client.address.id) == client_data["address"]["id"]
            assert client.address.line == client_data["address"]["line"]
            assert (
                client.address.neighborhood
                == client_data["address"]["neighborhood"]
            )
            assert client.address.city == client_data["address"]["city"]
            assert client.address.state == client_data["address"]["state"]
            assert client.address.country == client_data["address"]["country"]
            assert str(client.address.latitude) == str(
                client_data["address"]["latitude"]
            )
            assert str(client.address.longitude) == str(
                client_data["address"]["longitude"]
            )

    def tests_missing_clients(self, db_session: Session):
        """
        Test GetClientsConsumer with a valid payload and verify the data.
        """
        consumer = GetClientsConsumer()
        valid_payload = {
            "client_ids": [
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                str(uuid.uuid4()),
            ]
        }
        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            clients_data = consumer.process_payload(valid_payload)
            clients_data = json.loads(clients_data)

        assert "clients" in clients_data
        assert len(clients_data["clients"]) == 0

    @pytest.mark.usefixtures("clients_in_db")
    def test_empty_clients(self, db_session: Session):
        """
        Test GetClientsConsumer with an empty list of product IDs.
        """
        consumer = GetClientsConsumer()
        valid_payload = {"client_ids": []}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            clients_data = consumer.process_payload(valid_payload)
            clients_data = json.loads(clients_data)

        assert "clients" in clients_data
        assert len(clients_data["clients"]) == 0

    def test_get_all_clients(
        self, db_session: Session, clients_in_db: list[User]
    ):
        """
        Test GetClientsConsumer with a valid payload and verify the data.
        """
        consumer = GetClientsConsumer()
        valid_payload = {"client_ids": None}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            clients_data = consumer.process_payload(valid_payload)
            clients_data = json.loads(clients_data)

        assert "clients" in clients_data
        assert len(clients_data["clients"]) == len(clients_in_db)
        assert {str(client.id) for client in clients_in_db} == {
            client["id"] for client in clients_data["clients"]
        }


class TestAuthUserConsumer:
    """
    Test suite for the AuthUserConsumer class.
    """

    def test_invalid_payload(self):
        """
        Test AuthUserConsumer with an invalid payload.
        """
        consumer = AuthUserConsumer()
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(
            response["error"], list
        )  # Validation errors are returned as a list
        assert response["error"][0]["loc"] == ("bearer_token",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self, db_session: Session, sellers_in_db: list[User]
    ):
        """
        Test AuthUserConsumer with a valid payload and verify the data.
        """
        consumer = AuthUserConsumer()
        seller = sellers_in_db[0]  # Select first seller
        token, _expires = create_access_token(seller)

        valid_payload = {"bearer_token": token}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            user_data = consumer.process_payload(valid_payload)
            user_data = json.loads(user_data)

        assert "user" in user_data
        user_data = user_data["user"]
        assert str(seller.id) == user_data["id"]
        assert seller.username == user_data["username"]
        assert seller.email == user_data["email"]
        assert seller.full_name == user_data["full_name"]
        assert seller.phone == user_data["phone"]
        assert seller.role == user_data["role"]
        assert user_data["address"] is None

    @pytest.mark.usefixtures("sellers_in_db")
    def test_invalid_token(self, db_session: Session):
        """
        Test AuthUserConsumer with an invalid token.
        """
        consumer = AuthUserConsumer()
        invalid_payload = {"bearer_token": "invalid_token"}

        with mock.patch("users.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            user_data = consumer.process_payload(invalid_payload)

        assert "user" in user_data
        assert user_data["user"] is None
