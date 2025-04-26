from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Query, Session, joinedload

from .models import Route
from .schemas import ListRoutesFilterSchema


def _base_routes_query(db: Session) -> Query:
    """
    Base query for routes.
    """
    return db.query(Route).options(joinedload(Route.stops))


def list_routes(db: Session, filters: ListRoutesFilterSchema) -> List[Route]:
    """
    Get all routes for a seller.
    """
    qs = _base_routes_query(db)
    if filters.seller_id:
        qs = qs.filter(Route.seller_id == filters.seller_id)
    if filters.client_id:
        qs = qs.filter(Route.stops.any(client_id=filters.client_id))
    if filters.start_date:
        qs = qs.filter(Route.date >= filters.start_date)
    if filters.end_date:
        qs = qs.filter(Route.date <= filters.end_date)

    return qs.order_by(Route.date.asc()).all()


def get_route_by_id(db: Session, route_id: UUID | date) -> Optional[Route]:
    """
    Get a route by its ID.
    """
    qs = _base_routes_query(db)
    if isinstance(route_id, date):
        qs = qs.filter(Route.date == route_id)
    else:
        qs = qs.filter(Route.id == route_id)

    return qs.first()
