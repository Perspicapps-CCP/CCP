from typing import Dict

from pydantic import ValidationError

from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .schemas import GetSellersResponseSchema, GetSllersSchema
from .services import get_sellers_with_ids


class GetSellersConsumer(BaseConsumer):
    """
    Consumer for getting sellers.
    """

    def __init__(self):
        super().__init__(queue="users.get_sellers")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all sellers.

        Args:
            data (Dict): The incoming seller ids.
        """
        db = SessionLocal()
        try:
            sellers_schema = GetSllersSchema.model_validate(payload)
            sellers = get_sellers_with_ids(db, sellers_schema.seller_ids)
            return GetSellersResponseSchema.model_validate(
                {"sellers": sellers}
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
