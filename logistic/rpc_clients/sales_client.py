import logging
from typing import Optional

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import CreateSaleDeliverySchema

logger = logging.getLogger(__name__)


class SalesClient(BaseRPCClient):

    def create_sale_delivery(
        self, data: CreateSaleDeliverySchema
    ) -> Optional[CreateSaleDeliverySchema]:
        """
        Create a sale delivery.
        """
        response = self.call_broker(
            "sales.create_sale_delivery",
            {
                "sale_id": str(data.sale_id),
                "delivery_id": str(data.delivery_id),
            },
        )
        if 'error' in response:
            logger.error(f"Error creating sale delivery: {response['error']}")
            return
        return CreateSaleDeliverySchema.model_validate(response)
