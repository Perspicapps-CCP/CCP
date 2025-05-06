import logging
from rpc_clients.schemas import DeliverySaleResponseSchema, DeliverySaleStatus, PayloadSaleSchema
from seedwork.base_rpc_client import BaseRPCClient


class LogisticClient(BaseRPCClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def send_pending_sales_orders_to_logistics(
        self, payload: PayloadSaleSchema
    ) -> bool:
        """
        publish pending sale order that need to be sent to logistics.
        """
        self.logger.info("Sending pending sales order to logistics service")
        self.logger.debug(f"Payload: {payload.model_dump_json()}")

        response = self.call_broker(
            "logistic.send_pending_sales_to_delivery", payload.model_dump_json()
        )
        self.logger.debug(f"Response: {response}")
        
        response = DeliverySaleResponseSchema.model_validate(response)

        if response.status == DeliverySaleStatus.SUCCESS:
            self.logger.info(response.message)
            return True
        else:
            self.logger.info(response.message)
            return False
