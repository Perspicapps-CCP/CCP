import json
import uuid
from unittest import mock

import pytest
from faker import Faker
from sqlalchemy.orm import Session
from users.consumers import GetSellersConsumer
from users.models import RoleEnum, User

fake = Faker()


@pytest.fixture
def sellers_in_db(db_session: Session) -> list[User]:
    """
    Fixture to create sellers in the database for testing.
    """
    sellers = [
        User(
            id=uuid.uuid4(),
            username=fake.user_name(),
            email=fake.email(),
            hashed_password=fake.password(length=12),
            full_name=fake.name(),
            phone=fake.phone_number(),
            role=RoleEnum.SELLER,
            is_active=True,
        )
        for _ in range(3)
    ]
    db_session.add_all(sellers)
    db_session.commit()
    return sellers


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
