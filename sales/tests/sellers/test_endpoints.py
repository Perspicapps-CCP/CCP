import datetime
from typing import List
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from rpc_clients.schemas import UserAuthSchema
from sellers.models import ClientForSeller, ClientVideo
from tests.conftest import generate_fake_sellers
import io

fake = Faker()


@pytest.fixture
def valid_payload():
    """
    Returns a valid payload for associating a client with a seller.
    """
    return {
        "client_id": str(fake.uuid4()),
    }


@pytest.fixture
def seller_id() -> UUID:
    """
    Fixture to provide a seller ID for authentication.
    """
    return UUID(fake.uuid4())


@pytest.fixture
def auth_client(client: TestClient, seller_id: UUID) -> TestClient:
    """
    Fixture to create a test client with authentication.
    """
    # Set up the authentication header
    auth_header = {"Authorization": f"Bearer {seller_id}"}
    client.headers.update(auth_header)
    return client


def test_unauthenticated_request(client: TestClient, valid_payload):
    """
    Test that an unauthenticated request returns a 401 Unauthorized error.
    """
    response = client.post(
        "/api/v1/sales/sellers/clients/", json=valid_payload
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_invalid_requester_role(
    auth_client: TestClient, valid_payload, monkeypatch
):
    """
    Test that a requester with an invalid role cannot associate a client with a seller.
    """

    def mock_get_auth_user(_self, token: str) -> UserAuthSchema:
        # Simulate a user with an invalid role
        seller = generate_fake_sellers([UUID(token)], with_address=True)[0]
        return UserAuthSchema(
            **seller.model_dump(),
            is_active=True,
            is_seller=False,
            is_client=True,
        )

    monkeypatch.setattr(
        "rpc_clients.users_client.UsersClient.auth_user",
        mock_get_auth_user,
    )

    payload = valid_payload.copy()
    response = auth_client.post(
        "/api/v1/sales/sellers/clients/", json=payload
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_missing_fields(auth_client: TestClient, valid_payload):
    """
    Test missing fields in the payload.
    """
    payload = valid_payload.copy()
    del payload["client_id"]  # Remove a required field
    response = auth_client.post(
        "/api/v1/sales/sellers/clients/", json=payload
    )
    assert response.status_code == 422
    assert "client_id" in response.json()["detail"][0]["loc"]


def test_invalid_client_id(
    auth_client: TestClient, valid_payload, monkeypatch
):
    """
    Test invalid client ID.
    """

    def mock_get_clients(self, client_ids):
        return []  # Simulate no clients found

    monkeypatch.setattr(
        "rpc_clients.users_client.UsersClient.get_clients",
        mock_get_clients,
    )
    payload = valid_payload.copy()
    response = auth_client.post(
        "/api/v1/sales/sellers/clients/", json=payload
    )
    assert response.status_code == 422
    assert "client_id" in response.json()["detail"][0]["loc"]


def test_client_already_associated(
    auth_client: TestClient,
    seed_clients_for_seller,
):
    """
    Test when a client is already associated with a seller.
    """
    client_for_seller = seed_clients_for_seller(1)[0]
    payload = {"client_id": str(client_for_seller.client_id)}

    response = auth_client.post(
        "/api/v1/sales/sellers/clients/", json=payload
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["client_id"]
    assert (
        "Client already associated with this seller"
        in response.json()["detail"][0]["msg"]
    )


def test_successful_creation(
    auth_client: TestClient, db_session: Session, valid_payload
):
    """
    Test successful creation of a client-seller association.
    """
    response = auth_client.post(
        "/api/v1/sales/sellers/clients/", json=valid_payload
    )
    assert response.status_code == 201

    # Verify the response contains the correct data
    response_data = response.json()
    assert response_data["client"]["id"] == valid_payload["client_id"]

    # Verify the client-seller association is inserted into the database
    db_client_for_seller = (
        db_session.query(ClientForSeller)
        .filter_by(client_id=UUID(valid_payload["client_id"]))
        .first()
    )
    assert db_client_for_seller is not None
    assert str(db_client_for_seller.client_id) == valid_payload["client_id"]


@pytest.fixture
def seed_clients_for_seller(db_session: Session, seller_id: UUID) -> callable:
    """
    Seed the database with client-seller associations for testing.

    Returns:
        Callable[[int], List[ClientForSeller]]:
          A function to seed client-seller associations.
    """

    def _seed_clients_for_seller(
        count: int = 2, seller: UUID = None
    ) -> List[ClientForSeller]:
        associations = []
        for _ in range(count):
            association = ClientForSeller(
                id=uuid4(),
                client_id=uuid4(),
                seller_id=seller or seller_id,
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
            )
            db_session.add(association)
            associations.append(association)
        db_session.commit()
        associations.sort(key=lambda x: x.created_at, reverse=True)
        return associations

    return _seed_clients_for_seller


def test_list_clients_for_seller_with_data(
    auth_client: TestClient, seed_clients_for_seller
):
    """
    Test the list clients endpoint when there are client-seller associations in the database.
    """
    associations = seed_clients_for_seller(3)  # Seed 3 associations
    # Add for other sellers
    for _ in range(2):
        seed_clients_for_seller(3, seller=uuid4())

    response = auth_client.get("/api/v1/sales/sellers/clients/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    for i, association in enumerate(associations):
        assert data[i]["id"] == str(association.id)
        assert data[i]["client"]["id"] == str(association.client_id)


def test_list_clients_for_seller_empty_database(auth_client: TestClient):
    """
    Test the list clients endpoint when the database is empty.
    """
    response = auth_client.get("/api/v1/sales/sellers/clients/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0


def test_was_visited_recently(
    auth_client: TestClient, seed_clients_for_seller, db_session: Session
):
    """
    Test the was_visited_recently field using the API by modifying the last_visited field.
    """
    # Seed a client-seller association
    associations = seed_clients_for_seller(2)
    # Update last_visited to within 24 hours
    associations[0].last_visited = (
        datetime.datetime.now() - datetime.timedelta(hours=23)
    )
    associations[1].last_visited = (
        datetime.datetime.now() - datetime.timedelta(hours=25)
    )
    db_session.commit()

    # Verify was_visited_recently is True
    response = auth_client.get("/api/v1/sales/sellers/clients/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == str(associations[0].id)
    assert data[0]["was_visited_recently"] is True
    assert data[1]["id"] == str(associations[1].id)
    assert data[1]["was_visited_recently"] is False


def test_register_client_visit_success(
    auth_client: TestClient, mock_storage_bucket: MagicMock, valid_payload
):

    file_content = b"test file content"
    file = ("test.txt", io.BytesIO(file_content), "text/plain")

    client_id = valid_payload["client_id"]

    response = auth_client.post(
        f"/api/v1/sales/sellers/clients/{client_id}/visit",
        data={"description": "Test visit"},
        files=[("attachments", file)],
    )

    assert response.status_code == 201
    mock_storage_bucket.blob.assert_called_once()
    json_data = response.json()
    assert "id" in json_data


def test_register_client_visit_validation_error(
    auth_client: TestClient, valid_payload
):
    client_id = valid_payload["client_id"]

    file_content = b"test file content"
    file = ("test.txt", io.BytesIO(file_content), "text/plain")

    response = auth_client.post(
        f"/api/v1/sales/sellers/clients/{client_id}/visit",
        data={},
        files=[("attachments", file)],
    )

    assert response.status_code == 422


def test_upload_client_video_success(
    auth_client: TestClient,
    mock_storage_bucket: MagicMock,
    db_session: Session,
    valid_payload,
):
    """
    Test successful upload of a client video.
    """
    # Arrange
    client_id = valid_payload["client_id"]
    title = "Test Video Title"
    description = "Test video description"
    file_content = b"fake video content"
    video_file = ("test_video.mp4", io.BytesIO(file_content), "video/mp4")

    # Act
    response = auth_client.post(
        f"/api/v1/sales/sellers/clients/{client_id}/videos",
        data={"title": title, "description": description},
        files=[("video", video_file)],
    )

    # Assert
    assert response.status_code == 201
    mock_storage_bucket.blob.assert_called_once()
    mock_storage_bucket.blob().upload_from_file.assert_called_once()

    json_data = response.json()
    assert "id" in json_data
    assert json_data["title"] == title
    assert json_data["description"] == description
    assert "url" in json_data
    assert "https://storage.googleapis.com/" in json_data["url"]
    assert "status" in json_data

    db_video = (
        db_session.query(ClientVideo)
        .filter_by(id=UUID(json_data["id"]))
        .first()
    )
    assert db_video is not None
    assert db_video.title == title
    assert db_video.description == description


def test_upload_client_video_storage_error(
    mock_storage_bucket: MagicMock, auth_client: TestClient, valid_payload
):
    """
    Test handling of storage service errors.
    """
    # Arrange
    mock_storage_bucket.blob().upload_from_file.side_effect = TimeoutError(
        "TimeoutError"
    )

    client_id = valid_payload["client_id"]
    file_content = b"test video content"
    video_file = ("test_video.mp4", io.BytesIO(file_content), "video/mp4")

    # Act
    response = auth_client.post(
        f"/api/v1/sales/sellers/clients/{client_id}/videos",
        data={"title": "Test", "description": "Test description"},
        files=[("video", video_file)],
    )

    # Assert
    assert response.status_code >= 500


def test_get_client_video_success_with_records(
    auth_client: TestClient,
    db_session: Session,
):
    db_client_video = ClientVideo(
        id=uuid4(),
        client_id=uuid4(),
        title=fake.sentence(),
        description=fake.sentence(),
        url=f"gs://mybucket/myfolder/{uuid4()}/video.mp4",
        status="PENDING",
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )
    db_session.add(db_client_video)
    db_session.commit()

    response = auth_client.get(
        f"/api/v1/sales/sellers/clients/{db_client_video.client_id}/videos"
    )

    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == str(db_client_video.id)
    assert response.json()[0]["status"] == db_client_video.status
    assert "mybucket/myfolder/" in response.json()[0]["url"]


def test_get_client_video_success_without_records(
    auth_client: TestClient,
):
    response = auth_client.get(
        f"/api/v1/sales/sellers/clients/{uuid4()}/videos"
    )

    assert response.status_code == 200
    assert len(response.json()) == 0
