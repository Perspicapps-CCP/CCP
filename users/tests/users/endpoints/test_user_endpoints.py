import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from users.auth import verify_password
from users.models import RoleEnum, User

fake = Faker()


@pytest.fixture
def user_payload() -> dict:
    """
    Fixture to generate a user payload using Faker.
    """
    return {
        "username": fake.user_name(),
        "full_name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "id_type": "CC",
        "identification": fake.ssn(),
        "password": "P@ssw0rd!",
        "address": {
            "id": fake.uuid4(),
            "line": fake.street_address(),
            "neighborhood": fake.street_name(),
            "city": fake.city(),
            "state": fake.state(),
            "country": fake.country(),
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude()),
        },
    }


def test_create_user(
    client: TestClient, user_payload: dict, db_session: Session
) -> None:
    """
    Test creating a new user and verify it is saved in the database.
    """
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 201
    assert response.json()["username"] == user_payload["username"]

    # Verify the user is saved in the database
    user = (
        db_session.query(User)
        .filter_by(username=user_payload["username"])
        .first()
    )
    assert user is not None
    assert user.username == user_payload["username"]
    assert user.email == user_payload["email"]
    assert user.role == RoleEnum.CLIENT

    # Check if the password is hashed
    assert user.hashed_password != user_payload["password"]
    assert verify_password(user_payload["password"], user.hashed_password)


def test_create_user_with_invalid_address(
    client: TestClient, user_payload: dict
) -> None:
    """
    Test creating a user with an invalid address.
    """
    user_payload["address"][
        "latitude"
    ] = "invalid_latitude"  # Invalid latitude
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["address", "latitude"] for e in errors)


def test_create_user_with_existing_fields(
    client: TestClient, user_payload: dict, db_session: Session
) -> None:
    """
    Test creating a user with already used fields
      (e.g., username, email, phone).
    """
    # Create the first user
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 201

    # Attempt to create another user with the same username, email, and phone
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 3
    assert any(
        e["msg"] == "Value error, Username is already taken." for e in errors
    )
    assert any(
        e["msg"] == "Value error, Email is already taken." for e in errors
    )
    assert any(
        e["msg"] == "Value error, Phone number is already taken."
        for e in errors
    )

    # Verify no duplicate users are created in the database
    users = (
        db_session.query(User)
        .filter_by(username=user_payload["username"])
        .all()
    )
    assert len(users) == 1


def test_create_user_with_invalid_password(
    client: TestClient, user_payload: dict
) -> None:
    """
    Test creating a user with an invalid password.
    """
    user_payload["password"] = "short"  # Invalid password (too short)
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["password"] for e in errors)
    assert any(
        e["msg"]
        == "Value error, Password must be at least 8 characters long."
        for e in errors
    )

    user_payload["password"] = (
        "NoSpecialChar123"  # Invalid password (no special character)
    )
    response = client.post("/api/v1/users/clients/", json=user_payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["password"] for e in errors)
    assert any(
        e["msg"]
        == "Value error, Password must include at least one special character."
        for e in errors
    )
