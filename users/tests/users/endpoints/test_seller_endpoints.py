import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from users.auth import get_password_hash
from users.models import RoleEnum, User

fake = Faker()


@pytest.fixture
def staff_user(db_session: Session) -> User:
    """
    Fixture to create a staff user for testing.
    """
    user = User(
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash("staff_password"),
        full_name=fake.name(),
        role=RoleEnum.STAFF,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def non_staff_user(db_session: Session) -> User:
    """
    Fixture to create a non-staff user for testing.
    """
    user = User(
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash("non_staff_password"),
        full_name=fake.name(),
        role=RoleEnum.BUYER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_token(client: TestClient, staff_user: User) -> str:
    """
    Fixture to get an authentication token for the staff user.
    """
    login_data = {
        "username": staff_user.username,
        "password": "staff_password",
    }
    response = client.post("/api/v1/users/login/", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def non_staff_auth_token(client: TestClient, non_staff_user: User) -> str:
    """
    Fixture to get an authentication token for a non-staff user.
    """
    login_data = {
        "username": non_staff_user.username,
        "password": "non_staff_password",
    }
    response = client.post("/api/v1/users/login/", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def headers(auth_token: str) -> dict:
    """
    Fixture to provide headers with the Authorization token.
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def seller_payload() -> dict:
    """
    Fixture to generate a seller payload using Faker.
    """
    return {
        "username": fake.user_name(),
        "full_name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "id_type": "CC",
        "identification": fake.ssn(),
    }


def test_list_sellers(client: TestClient, headers: dict) -> None:
    """
    Test listing all sellers with valid authentication.
    """
    response = client.get("/api/v1/users/sellers", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_seller(
    client: TestClient,
    headers: dict,
    seller_payload: dict,
    db_session: Session,
) -> None:
    """
    Test creating a new seller with valid authentication
      and verify it is saved in the database.
    """
    response = client.post(
        "/api/v1/users/sellers", json=seller_payload, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["username"] == seller_payload["username"]

    # Verify the seller is saved in the database
    seller = (
        db_session.query(User)
        .filter_by(username=seller_payload["username"])
        .first()
    )
    assert seller is not None
    assert seller.username == seller_payload["username"]
    assert seller.email == seller_payload["email"]
    assert seller.role == RoleEnum.SELLER


def test_create_seller_with_existing_fields(
    client: TestClient,
    headers: dict,
    seller_payload: dict,
    db_session: Session,
) -> None:
    """
    Test creating a seller with already used fields
      (e.g., username, email) and verify
        the database state.
    """
    # Create the first seller
    response = client.post(
        "/api/v1/users/sellers", json=seller_payload, headers=headers
    )
    assert response.status_code == 201

    # Attempt to create another seller with the same username and email
    response = client.post(
        "/api/v1/users/sellers", json=seller_payload, headers=headers
    )
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
    # Verify no duplicate sellers are created in the database
    sellers = (
        db_session.query(User)
        .filter_by(username=seller_payload["username"])
        .all()
    )
    assert len(sellers) == 1


def test_sellers_with_incorrect_auth(client: TestClient) -> None:
    """
    Test accessing sellers endpoints with incorrect or missing authentication.
    """
    # Missing authentication
    response = client.get("/api/v1/users/sellers")
    assert response.status_code == 401

    # Incorrect authentication
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/users/sellers", headers=headers)
    assert response.status_code == 401


def test_sellers_with_non_staff_user(
    client: TestClient,
    non_staff_auth_token: str,
    seller_payload: dict,
    db_session: Session,
) -> None:
    """
    Test accessing sellers endpoints with a user that
      does not have the STAFF role.
    """
    headers = {"Authorization": f"Bearer {non_staff_auth_token}"}

    # Attempt to list sellers
    response = client.get("/api/v1/users/sellers", headers=headers)
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You do not have permission to perform this action."
    )

    # Attempt to create a seller
    response = client.post(
        "/api/v1/users/sellers", json=seller_payload, headers=headers
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You do not have permission to perform this action."
    )

    # Verify no seller is created in the database
    seller = (
        db_session.query(User)
        .filter_by(username=seller_payload["username"])
        .first()
    )
    assert seller is None
