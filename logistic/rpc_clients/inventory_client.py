from rpc_clients.schemas import (
    GetWarehousesResponseSchema,
    WarehouseSchema,
)
from seedwork.base_rpc_client import BaseRPCClient


class InventoryClient(BaseRPCClient):

    def get_warehouses(self) -> list[WarehouseSchema]:
        """
        Get all warehouses.
        """
        response = self.call_broker("inventory.get_warehouses", {})

        if not response:
            return []

        response = GetWarehousesResponseSchema.model_validate(response)
        return response.warehouses
