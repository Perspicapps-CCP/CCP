from fastapi.testclient import TestClient


def test_reset_db(
    client: TestClient,
) -> None:
    """
    Test reset endpoint
    """
    # Arrange

    # Act
    response = client.post("/inventory/reset")

    # Assert
    assert response.status_code == 200


def test_get_health(
    client: TestClient,
) -> None:
    """
    Test health endpoint
    """
    # Arrange

    # Act
    response = client.get("/inventory/health")

    # Assert
    assert response.status_code == 200
