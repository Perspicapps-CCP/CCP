import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from rpc_clients.users_client import UsersClient

from .models import Route, Stop


def seed_routes(db: Session):
    """
    Create sales with users.

    Args:
        db (Session): The database session.
    """
    if db.query(func.count(Route.id)).scalar() > 0:
        return
    # Bring all sellers
    sellers = UsersClient().get_all_sellers()
    # Bring all clients
    clients = UsersClient().get_all_clients()

    # To each seller add a route with all the clients.
    # Do this for the next 3 months.
    for seller in enumerate(sellers):
        for i in range(90):
            # Create a route for the seller
            route = Route(
                id=uuid.uuid4(),
                date=datetime.now() + timedelta(days=i),
                seller_id=seller[1].id,
            )
            db.add(route)
            # Create stops for the route
            for client in clients:
                if not client.address:
                    continue
                stop = Stop(
                    id=uuid.uuid4(),
                    route_id=route.id,
                    client_id=client.id,
                )
                db.add(stop)
    db.commit()
