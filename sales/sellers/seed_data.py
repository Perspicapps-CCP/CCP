import faker
from sqlalchemy import func
from sqlalchemy.orm import Session

from rpc_clients.users_client import UsersClient

from .models import ClientForSeller

fake = faker.Faker()


def seed_seller_clients(db: Session):
    """
    Create sales with users.

    Args:
        db (Session): The database session.
    """
    if db.query(func.count(ClientForSeller.id)).scalar() > 0:
        return
    # Bring all sellers
    sellers = UsersClient().get_all_sellers()
    # Bring all clients
    clients = UsersClient().get_all_clients()

    # To each seller add a route with all the clients.
    # Do this for the next 3 months.
    for seller in sellers:
        for client in clients:
            if fake.boolean(50):
                continue
            relation = ClientForSeller(
                client_id=client.id,
                seller_id=seller.id,
                last_visited=fake.date_time().date(),
            )
            db.add(relation)
    db.commit()
