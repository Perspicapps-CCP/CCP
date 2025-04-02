from typing import Dict

from config import CREATE_DELIVERY_TOPIC
from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .mappers import delivery_to_schema
from .schemas import DeliveryCreateSchema
from .services import create_delivery


class CreateDeliveryConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(queue=CREATE_DELIVERY_TOPIC)

    def process_payload(self, payload: Dict) -> Dict:
        db = SessionLocal()
        try:
            delivery_schema = DeliveryCreateSchema(**payload)
            delivery = create_delivery(db, delivery_schema)
            return delivery_to_schema(delivery).model_dump_json()
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
