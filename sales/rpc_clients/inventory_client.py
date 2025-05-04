from seedwork.base_rpc_client import BaseRPCClient

from .schemas import ReserveStockSchema


class InventoryClient(BaseRPCClient):

    def reserve_stock(self, payload: ReserveStockSchema):
        """
        Reserve stock for a given order.
        """

        response = self.call_broker("inventory.reserve_stock", payload)
        return response
