from typing import List
from uuid import UUID as UUUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import SellerSchema


class UsersClient(BaseRPCClient):
    """
    Client to interact with the users service.
    """

    def get_sellers(self, seller_ids: List[UUUID]) -> List[SellerSchema]:
        """
        Get user by id.
        """
        payload = {"seller_ids": [str(id) for id in seller_ids]}
        response = self.call_broker("users.get_sellers", payload)
        return [
            SellerSchema.model_validate(seller)
            for seller in response["sellers"]
        ]
