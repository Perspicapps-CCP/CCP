import datetime
from itertools import cycle
from typing import Callable, List, Optional
from uuid import UUID

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from routes.models import Route, Stop

fake = Faker()


@pytest.fixture
def seller_ids() -> List[UUID]:
    """
    Fixture to provide a list of seller IDs.
    """
    return [UUID(fake.uuid4()) for _ in range(2)]


@pytest.fixture
def seed_routes(
    db_session: Session,
    seller_ids: List[UUID],
) -> Callable[[int, Optional[int]], List[Route]]:
    sellers = cycle(seller_ids)

    def _seed_routes(
        count: int = 10, stops_per_route: int = 2
    ) -> List[Route]:
        routes = []
        for i in range(count):
            route = Route(
                id=UUID(fake.uuid4()),
                seller_id=next(sellers),
                date=datetime.date.today() + datetime.timedelta(days=i),
            )
            db_session.add(route)
            db_session.commit()

            for _ in range(stops_per_route):
                stop = Stop(
                    id=UUID(fake.uuid4()),
                    route_id=route.id,
                    client_id=UUID(fake.uuid4()),
                )
                db_session.add(stop)
            routes.append(route)
        db_session.commit()

        routes.sort(key=lambda x: x.date)

        return routes

    return _seed_routes


@pytest.fixture
def seller_id(
    seller_ids: List[UUID],
) -> UUID:
    """
    Fixture to provide a single seller ID.
    """
    return seller_ids[0]


@pytest.fixture
def auth_client(
    client: TestClient,
    seller_id: UUID,
) -> TestClient:
    """
    Fixture to create a test client with authentication.
    """
    # Set up the authentication header
    auth_header = {
        "Authorization": f"Bearer {seller_id}",
    }
    # Create a new TestClient with the auth header
    client.headers.update(auth_header)
    return client


def test_no_auth_header(
    client: TestClient,
) -> None:
    # Make a request to the endpoint without an auth header
    response = client.get(
        "api/v1/sales/routes/",
    )

    # Check the response status code
    assert response.status_code == 401

    # Check the response data
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_invalid_auth_header(
    client: TestClient,
) -> None:
    # Make a request to the endpoint with an invalid auth header
    response = client.get(
        "api/v1/sales/routes/",
        headers={"Authorization": "Bearer invalid_token"},
    )

    # Check the response status code
    assert response.status_code == 401

    # Check the response data
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_malformed_auth_header(
    client: TestClient,
) -> None:
    # Make a request to the endpoint with a malformed auth header
    response = client.get(
        "api/v1/sales/routes/",
        headers={"Authorization": "Bearer "},
    )
    # Check the response status code
    assert response.status_code == 401
    # Check the response data
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_list_routes_for_seller(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=5)

    seller_routes = [
        route for route in routes if route.seller_id == seller_id
    ]
    assert len(seller_routes) > 0

    # Make a request to the endpoint
    response = auth_client.get(
        "api/v1/sales/routes/",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert len(data) == len(seller_routes)

    for route_response, route in zip(data, seller_routes):
        assert route_response["id"] == str(route.id)
        assert route_response["date"] == route.date.strftime("%Y-%m-%d")
        assert route_response["created_at"] == route.created_at.isoformat()
        assert route_response["updated_at"] == route.updated_at.isoformat()
        assert len(route_response["stops"]) == len(route.stops)
        stops_by_id = {str(stop.id): stop for stop in route.stops}
        for stop_response in route_response["stops"]:
            stop = stops_by_id[stop_response["id"]]
            assert stop_response["client"]["id"] == str(stop.client_id)
            assert (
                stop_response["address"]["id"]
                == stop_response["client"]["address"]["id"]
            )
            assert stop_response["created_at"] == stop.created_at.isoformat()
            assert stop_response["updated_at"] == stop.updated_at.isoformat()


def test_filter_route_by_client_id(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=5)
    routes = [route for route in routes if route.seller_id == seller_id]

    # Get the first route
    route = routes[0]

    # Make a request to the endpoint with a client ID filter
    response = auth_client.get(
        f"api/v1/sales/routes/?client_id={route.stops[0].client_id}",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(route.id)


def test_filter_routes_by_start_date(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=10)
    routes = [route for route in routes if route.seller_id == seller_id]

    # Get the first route
    base_date = routes[0].date

    routes = [route for route in routes if route.date >= base_date]

    # Make a request to the endpoint with a start date filter
    response = auth_client.get(
        f"api/v1/sales/routes/?start_date={base_date.strftime('%Y-%m-%d')}",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert len(data) == len(routes)
    for route_response, route in zip(data, routes):
        assert route_response["id"] == str(route.id)
        assert route_response["date"] == route.date.strftime("%Y-%m-%d")


def test_filter_routes_by_end_date(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=10)
    routes = [route for route in routes if route.seller_id == seller_id]

    # Get the first route
    base_date = routes[0].date

    routes = [route for route in routes if route.date <= base_date]

    # Make a request to the endpoint with an end date filter
    response = auth_client.get(
        f"api/v1/sales/routes/?end_date={base_date.strftime('%Y-%m-%d')}",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert len(data) == len(routes)
    for route_response, route in zip(data, routes):
        assert route_response["id"] == str(route.id)
        assert route_response["date"] == route.date.strftime("%Y-%m-%d")


def test_empty_list_routes(
    auth_client: TestClient,
) -> None:
    # Make a request to the endpoint
    response = auth_client.get(
        "api/v1/sales/routes/",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert len(data) == 0


def test_get_route_by_id(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=5)
    routes = [route for route in routes if route.seller_id == seller_id]

    # Get the first route
    route = routes[0]

    # Make a request to the endpoint
    response = auth_client.get(
        f"api/v1/sales/routes/{route.id}/",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert data["id"] == str(route.id)
    assert data["date"] == route.date.strftime("%Y-%m-%d")
    assert len(data["stops"]) == len(route.stops)


def test_get_route_by_date(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=5)
    routes = [route for route in routes if route.seller_id == seller_id]

    # Get the first route
    route = routes[0]

    # Make a request to the endpoint
    response = auth_client.get(
        f"api/v1/sales/routes/{route.date.strftime('%Y-%m-%d')}/",
    )

    # Check the response status code
    assert response.status_code == 200

    # Check the response data
    data = response.json()
    assert data["id"] == str(route.id)
    assert data["date"] == route.date.strftime("%Y-%m-%d")
    assert len(data["stops"]) == len(route.stops)


def test_get_not_authorized_route(
    auth_client: TestClient,
    seed_routes: Callable[[int, Optional[int]], List[Route]],
    seller_id: UUID,
) -> None:
    # Seed the database with routes
    routes = seed_routes(count=5)

    # Get the first route
    route = [route for route in routes if route.seller_id != seller_id][0]

    # Make a request to the endpoint
    response = auth_client.get(
        f"api/v1/sales/routes/{route.id}/",
    )

    # Check the response status code
    assert response.status_code == 404

    # Check the response data
    data = response.json()
    assert data["detail"] == "Route not found"


def test_get_route_by_id_not_found(
    auth_client: TestClient,
) -> None:
    # Make a request to the endpoint with a non-existent route ID
    response = auth_client.get(
        f"api/v1/sales/routes/{UUID(fake.uuid4())}/",
    )

    # Check the response status code
    assert response.status_code == 404

    # Check the response data
    data = response.json()
    assert data["detail"] == "Route not found"
