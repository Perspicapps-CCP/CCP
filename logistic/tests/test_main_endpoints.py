from fastapi.testclient import TestClient


def test_reset_db(
    client: TestClient,
) -> None:
    """
    Test reset endpoint
    """
    # Arrange

    # Act
    response = client.post("/logistic/reset")

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
    response = client.get("/logistic/health")

    # Assert
    assert response.status_code == 200
