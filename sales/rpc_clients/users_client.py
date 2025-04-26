from typing import List, Optional
from uuid import UUID as UUUID

from seedwork.base_rpc_client import BaseRPCClient

from .schemas import UserAuthSchema, UserSchema


class UsersClient(BaseRPCClient):
    """
    Client to interact with the users service.
    """

    def get_sellers(
        self, seller_ids: Optional[List[UUUID]]
    ) -> List[UserSchema]:
        """
        Get user by id.
        """
        payload = {
            "seller_ids": (
                [str(id) for id in seller_ids] if seller_ids else None
            )
        }
        response = self.call_broker("users.get_sellers", payload)
        return [
            UserSchema.model_validate(seller)
            for seller in response["sellers"]
        ]

    def get_all_sellers(self) -> List[UserSchema]:
        """
        Get all sellers.
        """
        return self.get_sellers(None)

    def get_clients(
        self, client_ids: Optional[List[UUUID]]
    ) -> List[UserSchema]:
        """
        Get user by id.
        """
        payload = {
            "client_ids": (
                [str(id) for id in client_ids] if client_ids else None
            )
        }
        response = self.call_broker("users.get_clients", payload)
        return [
            UserSchema.model_validate(client)
            for client in response["clients"]
        ]

    def get_all_clients(self) -> List[UserSchema]:
        """
        Get all clients.
        """
        return self.get_clients(None)

    def auth_user(self, bearer_token: str) -> Optional[UserAuthSchema]:
        """
        Authenticate user.
        """
        response = self.call_broker(
            "users.auth_user", {"bearer_token": bearer_token}
        )
        if not response.get("user"):
            return None
        return UserAuthSchema.model_validate(response["user"])
