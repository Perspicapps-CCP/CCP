from typing import Dict

from pydantic import ValidationError

from config import CREATE_SELLER_TOPIC
from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .mappers import user_to_schema
from .schemas import CreateStaffSchema
from .services import create_seller


class CreateSellerConsumer(BaseConsumer):
    """
    Consumer for creating a new seller.
    """

    def __init__(self):
        super().__init__(queue=CREATE_SELLER_TOPIC)

    def process_payload(self, payload: Dict) -> Dict:
        db = SessionLocal()
        try:
            delivery_schema = CreateStaffSchema(**payload)
            delivery = create_seller(db, delivery_schema)
            return user_to_schema(delivery).model_dump_json()
        except ValidationError as e:
            # Return Pydantic validation errors as JSON
            return {"error": e.errors()}
        except Exception as e:
            # Handle other exceptions
            return {"error": str(e)}
        finally:
            db.close()
