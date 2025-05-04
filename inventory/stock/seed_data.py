
from faker import Faker
from sqlalchemy.orm import Session

from rpc_clients.suppliers_client import SuppliersClient
from warehouse.models import Warehouse

from .models import Stock

fake = Faker(["es_CO"])
fake.seed_instance(123)


def seed_stock(db: Session) -> None:
    if db.query(Stock).count() > 0:
        print("Stock already seeded")
        return
    warehouses = db.query(Warehouse).all()
    products = SuppliersClient().get_all_products()
    try:
        for warehouse in warehouses:
            for product in products:
                db_stock = Stock(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    quantity=fake.random_int(min=10, max=100),
                )
                db.add(db_stock)
                db.commit()
                db.refresh(db_stock)

    except Exception as e:
        print(f"Error seeding stock: {e}")
