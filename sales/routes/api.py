import uuid
from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.api import get_auth_user
from db_dependency import get_db

from . import mappers, schemas, services

routes_router = APIRouter(prefix="/routes", tags=["Routes"])


@routes_router.get(
    "/",
    response_model=List[schemas.RouteDetailSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "List of all routes.",
        }
    },
)
def list_routes(
    filter_query: Annotated[schemas.ListRoutesFilterSchema, Query()],
    db: Session = Depends(get_db),
    user=Depends(get_auth_user),
) -> List[schemas.RouteDetailSchema]:
    """
    List all routes.
    """
    filter_query.seller_id = user.id
    routes = services.get_all_routes(db, filter_query)
    return mappers.routes_to_schema(routes)


@routes_router.get(
    "/{route_id}",
    response_model=schemas.RouteDetailSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Route details.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Route not found.",
        },
    },
)
def get_route(
    route_id: uuid.UUID | date,
    db: Session = Depends(get_db),
    user=Depends(get_auth_user),
) -> schemas.RouteDetailSchema:
    """
    Get route details.
    """
    route = services.get_route_by_id(db, route_id)
    if not route or route.seller_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
        )

    return mappers.route_to_schema(route)
