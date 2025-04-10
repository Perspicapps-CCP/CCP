from typing import List
from uuid import UUID as UUUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import ProductSchema


class SuppliersClient(BaseRPCClient):
    """
    Client to interact with the suppliers service.
    """

    def get_all_products(self) -> List[ProductSchema]:
        """
        Get user by id.
        """
        payload = {}
        response = self.call_broker("suppliers.get_products", payload)
        return [
            ProductSchema.model_validate(products)
            for products in response["products"]
        ]
