from typing import Dict

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from users.auth import get_password_hash
from users.models import RoleEnum, User

fake = Faker()
fake.seed_instance(0)


@pytest.fixture
def user_credentials() -> Dict:
    """
    Fixture to generate user credentials for testing authentication.
    """
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(length=12),
        "full_name": fake.name(),
        "phone": fake.phone_number(),
    }


@pytest.fixture
def multiple_users(db_session: Session) -> list:
    """
    Fixture to create multiple users in the database for testing.
    """
    users = []
    # Create 3 different users with known credentials
    for i in range(3):
        password = f"securepass{i}123!"
        hashed_password = get_password_hash(password)

        user = User(
            username=f"testuser{i}",
            email=f"testuser{i}@example.com",
            hashed_password=hashed_password,
            full_name=f"Test User {i}",
            phone=f"123-456-789{i}",
            role=RoleEnum.STAFF,
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        users.append(
            {
                "user_data": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "role": user.role,
                },
                "credentials": {
                    "username": user.username,
                    "password": password,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "role": user.role,
                },
            }
        )

    return users


@pytest.fixture
def registered_user(db_session: Session, user_credentials: Dict) -> Dict:
    """
    Fixture to create a registered user and return their credentials.
    """
    # Create the user directly using the User model
    hashed_password = get_password_hash(user_credentials["password"])

    user = User(
        username=user_credentials["username"],
        email=user_credentials["email"],
        hashed_password=hashed_password,
        full_name=user_credentials["full_name"],
        phone=user_credentials["phone"],
        role=RoleEnum.STAFF,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Return both the user data and the original credentials
    return {
        "user_data": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
        },
        "credentials": user_credentials,
    }


@pytest.fixture
def auth_token(client: TestClient, registered_user: Dict) -> str:
    """
    Fixture to get an authentication token for a registered user.
    """
    login_data = {
        "username": registered_user["credentials"]["username"],
        "password": registered_user["credentials"]["password"],
    }

    response = client.post("/api/v1/users/login/", json=login_data)
    assert response.status_code == 200

    return response.json()["access_token"]


# Login Tests
def test_login_valid_credentials(
    client: TestClient, registered_user: Dict
) -> None:
    """
    Test login with valid credentials.
    """
    login_data = {
        "username": registered_user["credentials"]["username"],
        "password": registered_user["credentials"]["password"],
    }

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Verify user identity in the response if available
    if "user" in response.json():
        user_data = response.json()["user"]
        assert (
            user_data["username"]
            == registered_user["credentials"]["username"]
        )
        assert user_data["email"] == registered_user["credentials"]["email"]
        assert "password" not in user_data

    # Use the token to get profile and verify it's the correct user
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    profile_response = client.get("/api/v1/users/profile/", headers=headers)
    assert profile_response.status_code == 200
    assert (
        profile_response.json()["username"]
        == registered_user["credentials"]["username"]
    )


def test_login_invalid_password(
    client: TestClient, registered_user: Dict
) -> None:
    """
    Test login with invalid password.
    """
    login_data = {
        "username": registered_user["credentials"]["username"],
        "password": "wrong_password",
    }

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 401
    assert "detail" in response.json()


def test_cross_user_password_validation(
    client: TestClient, multiple_users: list
) -> None:
    """
    Test that a user cannot login with another user's password.
    """
    # Try to login with user1's username but user2's password
    login_data = {
        "username": multiple_users[0]["credentials"]["username"],
        "password": multiple_users[1]["credentials"]["password"],
    }

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_multiple_users(
    client: TestClient, multiple_users: list
) -> None:
    """
    Test login with different valid user credentials.
    """
    # Try to log in with each user from our multiple_users fixture
    for user in multiple_users:
        login_data = {
            "username": user["credentials"]["username"],
            "password": user["credentials"]["password"],
        }

        response = client.post("/api/v1/users/login/", json=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"

        # Verify user identity with the token
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        profile_response = client.get(
            "/api/v1/users/profile/", headers=headers
        )
        assert profile_response.status_code == 200
        assert (
            profile_response.json()["username"]
            == user["credentials"]["username"]
        )
        assert (
            profile_response.json()["email"] == user["credentials"]["email"]
        )
        assert profile_response.json()["role"] == user["credentials"]["role"]


def test_login_nonexistent_user(client: TestClient) -> None:
    """
    Test login with a username that doesn't exist.
    """
    login_data = {
        "username": fake.user_name(),
        "password": fake.password(),
    }

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_missing_username(client: TestClient) -> None:
    """
    Test login with missing username.
    """
    login_data = {"password": fake.password()}

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 422  # Validation error


def test_login_missing_password(
    client: TestClient, registered_user: Dict
) -> None:
    """
    Test login with missing password.
    """
    login_data = {"username": registered_user["credentials"]["username"]}

    response = client.post("/api/v1/users/login/", json=login_data)

    assert response.status_code == 422  # Validation error


# Profile Tests
def test_get_profile_valid_token(
    client: TestClient, auth_token: str, registered_user: Dict
) -> None:
    """
    Test getting user profile with a valid token.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/api/v1/users/profile/", headers=headers)

    assert response.status_code == 200
    assert (
        response.json()["username"]
        == registered_user["user_data"]["username"]
    )
    assert response.json()["email"] == registered_user["user_data"]["email"]
    assert (
        response.json()["full_name"]
        == registered_user["user_data"]["full_name"]
    )
    assert response.json()["phone"] == registered_user["user_data"]["phone"]
    assert response.json()["role"] == registered_user["user_data"]["role"]
    assert "password" not in response.json()


def test_get_profile_invalid_token(client: TestClient) -> None:
    """
    Test getting user profile with an invalid token.
    """
    headers = {"Authorization": "Bearer invalidtoken123"}

    response = client.get("/api/v1/users/profile/", headers=headers)

    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_profile_missing_token(client: TestClient) -> None:
    """
    Test getting user profile without providing a token.
    """
    response = client.get("/api/v1/users/profile/")

    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_profile_expired_token(client: TestClient) -> None:
    """
    Test getting user profile with an expired token (simulated).
    """
    # This is a simulated expired JWT token
    expired_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE1MTYyMzkwMjJ9."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )

    headers = {"Authorization": f"Bearer {expired_token}"}

    response = client.get("/api/v1/users/profile/", headers=headers)

    assert response.status_code == 401
    assert "detail" in response.json()
