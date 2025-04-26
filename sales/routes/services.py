from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from . import crud, models, schemas


def get_all_routes(
    db: Session,
    filters: schemas.ListRoutesFilterSchema,
) -> List[models.Route]:
    """
    Get all routes for a seller.
    """
    routes = crud.list_routes(db, filters)
    return routes


def get_route_by_id(
    db: Session,
    route_id: UUID | date,
) -> models.Route:
    """
    Get a route by its ID.
    """
    route = crud.get_route_by_id(db, route_id)
    return route
