import logging
from typing import Dict

from pydantic import ValidationError

from database import SessionLocal
from delivery.mappers import deliveries_to_aggregation
from delivery.schemas import (
    DeliverySaleResponseSchema,
    DeliverySaleStatus,
    GetDeliveriesResponseSchema,
    GetDelivieriesSchema,
    PayloadSaleSchema,
)
from delivery.services import (
    create_delivery_stops_transaction,
    get_deliveries_by_ids,
)
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient
from seedwork.base_consumer import BaseConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)


class CreateDeliveryStopsConsumer(BaseConsumer):
    """
    Consumer for processing sales data and creating delivery items.
    This consumer listens to the queue
    "logistic.send_pending_sales_to_delivery"
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
            sale_payload = PayloadSaleSchema.model_validate(payload)
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
        except ValidationError as e:
            logger.exception(f"Error processing payload: {str(e)}")
            return DeliverySaleResponseSchema(
                sale_id=None,
                status=DeliverySaleStatus.ERROR,
                message=str(e.errors()),
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


class GetDeliveriesConsumer(BaseConsumer):
    """
    Consumer for getting deliveries.
    """

    def __init__(self):
        super().__init__(queue="logistic.get_deliveries")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all deliveries.

        Args:
            data (Dict): The incoming deliveries ids.
        """
        db = SessionLocal()
        try:
            deliveries_schema = GetDelivieriesSchema.model_validate(payload)
            deliveries = get_deliveries_by_ids(
                db, deliveries_schema.deliveries_ids
            )
            # Sort deliveries by id position in payload
            if deliveries_schema.deliveries_ids:
                deliveries.sort(
                    key=lambda x: (
                        deliveries_schema.deliveries_ids.index(x.id)
                        if x.id in deliveries_schema.deliveries_ids
                        else -1
                    )
                )
            return GetDeliveriesResponseSchema(
                **{
                    "deliveries": deliveries_to_aggregation(
                        deliveries, db, InventoryClient(), SuppliersClient()
                    )
                }
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
