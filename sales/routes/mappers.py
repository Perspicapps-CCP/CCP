from typing import Dict, List
from uuid import UUID

from rpc_clients.schemas import UserSchema
from rpc_clients.users_client import UsersClient

from .models import Route
from .schemas import RouteDetailSchema, StopSchema


def _route_to_schema(
    route: Route,
    clients: Dict[UUID, UserSchema],
) -> RouteDetailSchema:
    """
    Convert a Route object to a RouteDetailSchema object.
    """
    return RouteDetailSchema(
        id=route.id,
        date=route.date,
        created_at=route.created_at,
        updated_at=route.updated_at,
        stops=[
            StopSchema(
                id=stop.id,
                client=clients[stop.client_id],
                address=clients[stop.client_id].address,
                created_at=stop.created_at,
                updated_at=stop.updated_at,
            )
            for stop in route.stops
        ],
    )


def route_to_schema(
    route: Route,
) -> RouteDetailSchema:
    """
    Convert a Route object to a RouteDetailSchema object.
    """
    return routes_to_schema([route])[0]


def routes_to_schema(
    routes: list[Route],
) -> List[RouteDetailSchema]:
    """
    Convert a list of Route objects to a list of RouteDetailSchema objects.
    """

    # Bring the clients
    clients = UsersClient().get_clients(
        list({stop.client_id for route in routes for stop in route.stops})
    )
    clients = {client.id: client for client in clients}

    return [_route_to_schema(route, clients) for route in routes]
