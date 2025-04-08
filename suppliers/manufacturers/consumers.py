from typing import Dict

from pydantic import ValidationError

from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .mappers import product_to_schema
from .schemas import GetProductsResponseSchema, GetProductsSchema
from .services import get_products


class GetProductsConsumer(BaseConsumer):
    """
    Consumer for getting sellers.
    """

    def __init__(self):
        super().__init__(queue="suppliers.get_products")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all sellers.

        Args:
            data (Dict): The incoming seller ids.
        """
        db = SessionLocal()
        try:
            products_schema = GetProductsSchema.model_validate(payload)
            products = get_products(
                db, productsIds=products_schema.product_ids
            )
            # Sort sellers by id position in payload
            products.sort(
                key=lambda x: (
                    products_schema.product_ids.index(x.id)
                    if x.id in products_schema.product_ids
                    else -1
                )
            )
            return GetProductsResponseSchema.model_validate(
                {
                    "products": [
                        product_to_schema(product) for product in products
                    ]
                }
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
