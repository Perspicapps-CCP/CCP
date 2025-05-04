import uuid
from itertools import cycle

from sqlalchemy import func
from sqlalchemy.orm import Session

from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

from .models import Sale, SaleItem


def seed_sales(db: Session):
    """
    Create sales with users.

    Args:
        db (Session): The database session.
    """
    if db.query(func.count(Sale.id)).scalar() > 0:
        return
    # Bring all sellers
    sellers = UsersClient().get_all_sellers()
    # Bring all clients
    clients = UsersClient().get_all_clients()
    cycle_clients = cycle(clients)
    # Bring all products
    products = SuppliersClient().get_all_products()[:3]

    total = sum(
        [product.price * (i + 1) for i, product in enumerate(products)]
    )

    # Create one sale for each seller with two items
    for i, seller in enumerate(sellers):
        # Create sale
        client = next(cycle_clients)
        sale_uuid = uuid.uuid4()
        sale = Sale(
            id=sale_uuid,
            seller_id=seller.id,
            client_id=client.id,
            address_id=uuid.uuid4(),
            total_value=total,
            currency="USD",
            order_number=i + 1,
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)

        for i, product in enumerate(products):
            item = SaleItem(
                id=uuid.uuid4(),
                sale_id=sale.id,
                product_id=product.id,
                quantity=i + 1,
                unit_price=product.price,
                total_value=(i + 1) * product.price,
            )
            db.add(item)
            db.commit()
