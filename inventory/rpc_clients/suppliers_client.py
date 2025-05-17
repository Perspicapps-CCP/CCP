from typing import List, Optional
from uuid import UUID as UUUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import ProductSchema


class SuppliersClient(BaseRPCClient):
    """
    Client to interact with the suppliers service.
    """

    def get_products(
        self, product_ids: Optional[List[UUUID]]
    ) -> List[ProductSchema]:
        """
         Fetch products by their ids.
        """
        payload = {
            "product_ids": (
                [str(id) for id in product_ids] if product_ids else None
            )
        }
        response = self.call_broker("suppliers.get_products", payload)
        return [
            ProductSchema.model_validate(products)
            for products in response["products"]
        ]

    def get_products_by_code(
        self, product_codes: List[str]
    ) -> List[ProductSchema]:
        """
        Fetch products by their codes.
        """
        payload = {"product_codes": product_codes}
        response = self.call_broker("suppliers.get_products_by_code", payload)
        return [
            ProductSchema.model_validate(products)
            for products in response["products"]
        ]

    def get_all_products(self) -> List[ProductSchema]:
        """
        Get all products.
        """
        return self.get_products(None)
