import uuid
import random
from faker import Faker

from deliveries.schemas import (
    DeliveryDetailGetResponseSchema,
    DeliveryItemGetResponseSchema,
    WarehouseSchema,
)


# Add to your schemas.py file
def create_mock_delivery_detail() -> DeliveryDetailGetResponseSchema:
    """Generate a mock delivery detail response with fake data"""
    fake = Faker(0)

    # Create fake warehouse data
    warehouse = WarehouseSchema(
        warehouse_id=uuid.uuid4(), warehouse_name=f"Warehouse {fake.city()}"
    )

    # Create fake delivery orders (1-5 items)
    orders = []
    for _ in range(random.randint(1, 10)):
        product_name = fake.word().capitalize() + " " + fake.word()
        orders.append(
            DeliveryItemGetResponseSchema(
                order_number=str(uuid.uuid4()),
                order_address=fake.address(),
                customer_phone_number=fake.phone_number(),
                product_code=f"PRD-{fake.bothify('??###')}",
                product_name=product_name,
                quantity=random.randint(1, 10),
                images=[
                    f"https://picsum.photos/id/{random.randint(1, 1000)}/600/400"
                    for _ in range(random.randint(1, 5))
                ],
            )
        )

    # Create fake delivery response
    delivery_statuses = ["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELED"]
    created_at = fake.date_time_between(start_date="-30d", end_date="now")

    return DeliveryDetailGetResponseSchema(
        shipping_number=fake.bothify("FDX##########"),
        license_plate=fake.bothify("??-####"),
        diver_name=fake.name(),
        warehouse=warehouse,
        delivery_status=random.choice(delivery_statuses),
        created_at=created_at,
        updated_at=fake.date_time_between(
            start_date=created_at, end_date="now"
        ),
        orders=orders,
    )
