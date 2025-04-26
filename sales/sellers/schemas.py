# Schema for plans data validation
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from rpc_clients.schemas import UserSchema
from rpc_clients.users_client import UsersClient

from .crud import does_client_for_seller_exist


class ErrorResponseSchema(BaseModel):
    detail: str


class ClientForSellerCreateSchema(BaseModel):
    client_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

    @field_validator("client_id")
    def validate_client_id(cls, client_id: uuid.UUID, values) -> uuid.UUID:
        """
        Validates the provided client ID by checking its existence.
        Args:
            client_id (uuid.UUID): The UUID of the client to validate.
        Returns:
            uuid.UUID: The validated client ID if it exists.
        Raises:
            ValueError: If the client ID is invalid or does not exist.
        """

        users_client = UsersClient()
        clients = users_client.get_clients([client_id])
        if len(clients) != 1:
            raise ValueError("Invalid client id.")
        context = values.context
        seller = context.get("seller")
        db = context.get("db")
        if (
            not db
            or not seller
            or does_client_for_seller_exist(db, seller.id, client_id)
        ):
            raise ValueError("Client already associated with this seller.")
        return client_id


class ClientForSellerDetailSchema(BaseModel):
    id: uuid.UUID
    client: UserSchema
    last_visited: Optional[datetime]
    was_visited_recently: bool
    client_thumbnail: str = Field(default="https://picsum.photos/128/128")
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
