from typing import List
from uuid import UUID as UUUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import ProductSchema


class SuppliersClient(BaseRPCClient):
    """
    Client to interact with the users service.
    """

    def get_products(self, product_ids: List[UUUID]) -> List[ProductSchema]:
        """
        Get user by id.
        """
        payload = {"product_ids": [str(id) for id in product_ids]}
        response = self.call_broker("suppliers.get_products", payload)
        return [
            ProductSchema.model_validate(products)
            for products in response["products"]
        ]

    def get_product(self, product_id: UUUID) -> ProductSchema:
        """
        Get user by id.
        """
        product = self.get_products([product_id])
        if not product:
            raise ValueError("Product not found.")
        return product[0]
