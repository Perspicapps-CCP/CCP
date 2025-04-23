import random
import re
from sqlalchemy.orm import Session
from faker import Faker

from warehouse.schemas import WarehouseSchema
from warehouse.services import create_warehouse

fake = Faker(['es_CO'])
fake.seed_instance(123)


def seed_warehouses(db: Session) -> None:
    try:
        warehouse_address = [
            "Costado Norte, Centro Empresarial Metropolitano, Km. 3.5, Siberia - Bogotá, Via Siberia #bodega 31, Bogotá, Cundinamarca",
            "Cra. 106 #15a-25, Bogotá",
            "Cra. 7c #182b -19, Bogotá",
            "Av Guayacanes #25, Bogotá",
            "Carrera 4 #58-44, Bogotá, Soacha, Cundinamarca",
        ]

        for i in range(5):
            warehouse = WarehouseSchema(
                warehouse_name=f"CCP Bodega Numero {i+1}",
                city="BOGOTA D.C.",
                country="COLOMBIA",
                address=warehouse_address[i],
                phone=''.join([str(random.randint(0, 9)) for _ in range(10)]),
            )
            create_warehouse(db, warehouse)
    except Exception as e:
        print(f"Error seeding warehouses: {e}")