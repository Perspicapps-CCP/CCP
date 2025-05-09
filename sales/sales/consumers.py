from typing import Dict

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .schemas import CreateSaleDeliverySchema
from .services import associate_delivery_to_sale


class CreateSaleDelivery(BaseConsumer):
    """
    Consumer for creating a sale delivery.
    """

    def __init__(self):
        super().__init__(queue="sales.create_sale_delivery")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all sellers.

        Args:
            data (Dict): The incoming seller ids.
        """
        db = SessionLocal()
        try:
            create_sale = CreateSaleDeliverySchema.model_validate(
                payload, context={"db": db}
            )
            associate_delivery_to_sale(
                db, create_sale.sale_id, create_sale.delivery_id
            )
            return create_sale.model_dump_json()
        except ValidationError as e:
            return {"error": jsonable_encoder(e.errors())}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
