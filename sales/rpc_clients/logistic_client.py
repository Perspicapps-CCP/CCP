from typing import List, Optional
from uuid import UUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import DeliverySchema, PayloadSaleSchema


class LogisticClient(BaseRPCClient):

    def send_pending_sales_to_delivery(self, payload: PayloadSaleSchema):
        """
        Send pending sales to delivery.
        """

        response = self.call_broker(
            "logistic.send_pending_sales_to_delivery", payload
        )
        return response

    def get_deliveries(self, deliveries_ids: Optional[List[UUID]]):
        """
        Get deliveries by ids.
        """
        response = self.call_broker(
            "logistic.get_deliveries",
            {
                "deliveries_ids": (
                    [str(delivery_id) for delivery_id in deliveries_ids]
                    if deliveries_ids
                    else None
                )
            },
        )
        return [
            DeliverySchema.model_validate(delivery)
            for delivery in response["deliveries"]
        ]
