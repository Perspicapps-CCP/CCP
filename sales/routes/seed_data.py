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
    from sellers.models import ClientForSeller

    if db.query(func.count(Route.id)).scalar() > 0:
        return

    all_relations = db.query(ClientForSeller).all()

    # Bring all sellers
    sellers = UsersClient().get_sellers(
        list({relation.seller_id for relation in all_relations})
    )
    # Bring all clients
    clients = {
        c.id: c
        for c in UsersClient().get_clients(
            list({relation.client_id for relation in all_relations})
        )
    }

    clients_by_seller = {
        seller.id: [
            relation.client_id
            for relation in all_relations
            if relation.seller_id == seller.id
        ]
        for seller in sellers
    }

    # To each seller add a route with all the clients.
    # Do this for the next 3 months.
    for seller_id, client_ids in clients_by_seller.items():
        for i in range(90):
            # Create a route for the seller
            route = Route(
                id=uuid.uuid4(),
                date=datetime.now() + timedelta(days=i),
                seller_id=seller_id,
            )
            db.add(route)
            # Create stops for the route
            for client_id in client_ids:
                client = clients[client_id]
                if not client.address:
                    continue
                stop = Stop(
                    id=uuid.uuid4(),
                    route_id=route.id,
                    client_id=client.id,
                )
                db.add(stop)
    db.commit()
