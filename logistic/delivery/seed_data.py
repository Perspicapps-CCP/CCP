import random
from datetime import datetime

from delivery import schemas
from delivery.services import (
    create_delivery_stops_transaction,
    create_delivery_transaction,
    create_driver,
)
from faker import Faker
from sqlalchemy.orm import Session

from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker(["es_CO"])
fake.seed_instance(123)


def create_pending_delivery_stops(db, products, warehouse, index):
    list_delivery_items = []
    for product in products:
        delivery_item = schemas.PayloadSaleItemSchema(
            sales_item_id=fake.uuid4(),
            product_id=product.id,
            warehouse_id=warehouse.warehouse_id,
            quantity=fake.random_int(min=1, max=10),
        )
        list_delivery_items.append(delivery_item)

    address = schemas.PayloadAddressSchema(
        id=fake.uuid4(),
        street=f"Calle {random.randint(1, 150)} #{random.randint(1, 120)}-{random.randint(1, 99)}",
        city="Bogotá",
        state="Bogotá D.C.",
        postal_code="110000",
        country="Colombia",
    )
    sale = schemas.PayloadSaleSchema(
        sales_id=fake.uuid4(),
        order_number=index + 1,
        address=address,
        sales_items=list_delivery_items,
    )
    create_delivery_stops_transaction(db, sale)
    return sale


def seed_delivery_data(db: Session):
    # create a fake driver
    for i in range(10):
        driver = schemas.DriverCreateSchema(
            driver_name=fake.name_male(),
            license_plate=fake.license_plate(),
            phone_number="".join(
                [str(random.randint(0, 9)) for _ in range(10)]
            ),
        )
        create_driver(db, driver)

    warehouses = InventoryClient().get_warehouses()[:-1]
    products = SuppliersClient().get_all_products()[:3]

    # create a fake list of pendieng delivery stops
    for warehouse in warehouses:
        for index in range(5):
            create_pending_delivery_stops(db, products, warehouse, index)

    warehouse = warehouses[-1]
    create_pending_delivery_stops(db, products, warehouse, 0)

    # create a fake delivery transaction for just one warehouse
    # with a available driver and delivery date
    request = schemas.DeliveryCreateRequestSchema(
        warehouse_id=warehouse.warehouse_id,
        delivery_date=datetime.now().date(),
    )

    create_delivery_transaction(db, request)
