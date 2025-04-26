import logging
from typing import Dict

from database import SessionLocal
from delivery.schemas import (
    DeliverySaleResponseSchema,
    DeliverySaleStatus,
    PayloadSaleSchema,
)
from delivery.services import create_delivery_stops_transaction
from seedwork.base_consumer import BaseConsumer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
)
logger = logging.getLogger(__name__)


class GetProductsConsumer(BaseConsumer):
    """
    Consumer for processing sales data and creating delivery items.
    This consumer listens to the queue "logistic.send_pending_sales_to_delivery"
    """

    def __init__(self):
        super().__init__(queue="logistic.send_pending_sales_to_delivery")

    def process_payload(self, payload: Dict) -> Dict:
        """
        Process the payload received from the queue.
        Args:
            payload (Dict): The payload received from the queue.
        """
        db = SessionLocal()
        try:
            logger.info(f"Processing payload: {payload}")
            sale_payload = PayloadSaleSchema.model_validate_json(payload)
            result = create_delivery_stops_transaction(db, sale_payload)

            if result:
                logger.info("Delivery items created successfully")
                return DeliverySaleResponseSchema(
                    sale_id=sale_payload.sales_id,
                    status=DeliverySaleStatus.SUCCESS,
                    message="Delivery items created successfully",
                ).model_dump_json()
            else:
                logger.error("Failed to create delivery items")
                return DeliverySaleResponseSchema(
                    sale_id=sale_payload.sales_id,
                    status=DeliverySaleStatus.ERROR,
                    message="Failed to create delivery items",
                ).model_dump_json()

        except Exception as e:
            logger.exception(f"Error processing payload: {str(e)}")
            return DeliverySaleResponseSchema(
                sale_id=sale_payload.sales_id,
                status=DeliverySaleStatus.ERROR,
                message=str(e),
            ).model_dump_json()
        finally:
            db.close()
