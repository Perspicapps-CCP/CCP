from seedwork.base_rpc_client import BaseRPCClient

from .schemas import PayloadSaleSchema


class LogisticClient(BaseRPCClient):

    def send_pending_sales_to_delivery(self, payload: PayloadSaleSchema):
        """
        Send pending sales to delivery.
        """

        response = self.call_broker(
            "logistic.send_pending_sales_to_delivery", payload
        )
        return response
