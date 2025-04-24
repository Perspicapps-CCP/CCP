import random
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from faker import Faker

from deliveries.schemas import DriverCreateSchema
from deliveries.services import (
    create_delivery_stops_transaction,
    create_driver,
    create_delivery_transaction,
    get_driver_available,
    update_driver_on_delivery,
)
from deliveries import schemas
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker(['es_CO'])
fake.seed_instance(123)


def seed_delivery_data(db: Session):
    # create a fake driver
    for i in range(10):
        driver = DriverCreateSchema(
            driver_name=fake.name_male(),
            license_plate=fake.license_plate(),
            phone_number=''.join(
                [str(random.randint(0, 9)) for _ in range(10)]
            ),
        )
        create_driver(db, driver)

    # make 3 deliveries for each warehouse (each delivery has 3 items)
    warehouses = InventoryClient().get_warehouses()[:3]
    products = SuppliersClient().get_all_products()[:3]

    # create a fake list of deliveries
    list_deliveries: List[schemas.PayloadSaleSchema] = []
    for warehouse in warehouses:
        for index in range(5):
            list_delivery_items = []
            for product in products:
                delivery_item = schemas.PayloadSaleItemSchema(
                    sales_item_id=fake.uuid4(),
                    product_id=product.id,
                    warehouse_id=warehouse.warehouse_id,
                )
                list_delivery_items.append(delivery_item)

            delivery = schemas.PayloadSaleSchema(
                sales_id=fake.uuid4(),
                order_number=index + 1,
                address_id=fake.uuid4(),
                address=f"Calle {random.randint(1, 150)} #{random.randint(1, 120)}-{random.randint(1, 99)}, Bogotá D.C., Colombia",
                sales_items=list_delivery_items,
            )
            create_delivery_stops_transaction(db, delivery)
            list_deliveries.append(delivery)

    # get all pending deliveries
    pending_deliveries = create_delivery_transaction(db)

    # if deliveries exist, then assign a driver to each delivery
    for delivery in pending_deliveries:
        driver = get_driver_available(db, datetime.now().date())
        if driver:
            update_driver_on_delivery(
                db, delivery.id, driver.id, datetime.now().date()
            )
