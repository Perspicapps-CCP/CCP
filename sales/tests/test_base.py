from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    """
    Test the /health endpoint returns correct status and response.
    """
    response = client.get("/api/v1/sales/health/")
    assert response.status_code == 200
    assert response.json() == "pong"


def test_reset_db_endpoint(client: TestClient) -> None:
    """
    Test the reset-db endpoint properly resets the database.
    """
    response = client.post("/api/v1/sales/reset-db/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Todos los datos fueron eliminados"}
