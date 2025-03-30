import json
from unittest.mock import patch

from sqlalchemy.orm import Session

from users.auth import verify_password
from users.consumers import CreateSellerConsumer
from users.models import User


def test_create_seller_consumer(
    db_session: Session,
):
    # Input data for the seller
    """
    Test the CreateSellerConsumer.process_payload method to ensure it
    processes the payload correctly and interacts with the database.
    """
    # No users before
    assert db_session.query(User).count() == 0

    # Mock payload
    payload = {
        "username": "seller_user",
        "full_name": "Seller User",
        "email": "seller_user@test.com",
        "phone_number": "1234567890",
        "password": "securepassword123#",
    }

    # Mock the SessionLocal to return the mocked database session
    with patch("users.consumers.SessionLocal", return_value=db_session):
        # Mock the create_seller function to return a User object

        # Instantiate the consumer
        consumer = CreateSellerConsumer()

        # Call process_payload
        result = consumer.process_payload(payload)
        assert isinstance(result, str), "Result should be a dictionary."

        result = json.loads(result)

        # Assertions
        assert result is not None, "Result should not be None."
        assert "username" in result, "Result should contain the username."
        assert result["username"] == payload["username"]
        assert result["email"] == payload["email"]
        assert result["role"] == "SELLER"
        assert db_session.query(User).count() == 1
        user = db_session.query(User).first()
        assert user.username == payload["username"]
        assert user.email == payload["email"]
        assert user.role == "SELLER"
        assert verify_password(
            payload["password"], user.hashed_password
        ), "Password should be hashed and verified correctly."


def test_create_seller_consumer_invalid_field_length(db_session: Session):
    """
    Test that CreateSellerConsumer.process_payload returns an error
    if any field exceeds the maximum length of 256 characters.
    """
    # Mock payload with an overly long username
    payload = {
        "username": "a" * 257,  # Exceeds 256 characters
        "full_name": "Seller User",
        "email": "seller_user@test.com",
        "phone_number": "1234567890",
        "password": "securepassword123#",
    }

    with patch("users.consumers.SessionLocal", return_value=db_session):
        consumer = CreateSellerConsumer()
        result = consumer.process_payload(payload)

        # Assertions
        assert "error" in result, "Result should contain an error."
        assert (
            result["error"][0]['loc'][0] == "username"
        ), "Error should mention the username."
        assert result["error"][0]['type'] == 'string_too_long'


def test_create_seller_consumer_invalid_email(db_session: Session):
    """
    Test that CreateSellerConsumer.process_payload returns an error
    if the email is invalid.
    """
    # Mock payload with an invalid email
    payload = {
        "username": "seller_user",
        "full_name": "Seller User",
        "email": "invalid-email",  # Invalid email format
        "phone_number": "1234567890",
        "password": "securepassword123#",
    }

    with patch("users.consumers.SessionLocal", return_value=db_session):
        consumer = CreateSellerConsumer()
        result = consumer.process_payload(payload)

        # Assertions
        assert "error" in result, "Result should contain an error."
        assert (
            result["error"][0]['loc'][0] == "email"
        ), "Error should mention the email."
        assert result["error"][0]['type'] == 'value_error'


def test_create_seller_consumer_invalid_password(db_session: Session):
    """
    Test that CreateSellerConsumer.process_payload returns an error
    if the password is invalid (e.g., too short).
    """
    # Mock payload with an invalid password
    payload = {
        "username": "seller_user",
        "full_name": "Seller User",
        "email": "seller_user@test.com",
        "phone_number": "1234567890",
        "password": "123",  # Too short
    }

    with patch("users.consumers.SessionLocal", return_value=db_session):
        consumer = CreateSellerConsumer()
        result = consumer.process_payload(payload)

        # Assertions
        assert "error" in result, "Result should contain an error."
        assert (
            result["error"][0]['loc'][0] == "password"
        ), "Error should mention the email."
        assert result["error"][0]['type'] == 'value_error'
