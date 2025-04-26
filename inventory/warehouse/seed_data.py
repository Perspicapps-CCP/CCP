import random
from sqlalchemy.orm import Session
from faker import Faker

from warehouse.models import Address, Warehouse

fake = Faker(['es_CO'])
fake.seed_instance(123)


def seed_warehouses(db: Session) -> None:
    try:
        warehouse_address = [
            {"addr": "Cra 116a #81-16", "lat": 4.725474, "lng": -74.121126},
            {"addr": "Cra 106 #15a-25", "lat": 4.671487, "lng": -74.155977},
            {"addr": "Cra 7c #182b -19", "lat": 4.759743, "lng": -74.028369},
            {"addr": "Av Guayacanes #25", "lat": 4.649275, "lng": -74.137076},
            {"addr": "Carrera 4 #58-44", "lat": 4.817069, "lng": -75.691937},
        ]

        for i in range(5):
            db_address = Address(
                street=warehouse_address[i]["addr"],
                city="BOGOTÁ",
                state="BOGOTA D.C.",
                country="COLOMBIA",
                latitude=warehouse_address[i]["lat"],
                longitude=warehouse_address[i]["lng"],
            )

            db.add(db_address)
            db.flush()

            db_warehouse = Warehouse(
                name=f"CCP Bodega Numero {i+1}",
                address_id=db_address.id,
                phone=''.join([str(random.randint(0, 9)) for _ in range(10)]),
            )
            db.add(db_warehouse)
            db.commit()
            db.refresh(db_warehouse)
    except Exception as e:
        print(f"Error seeding warehouses: {e}")
