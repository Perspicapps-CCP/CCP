from typing import Dict

from fastapi import HTTPException
from pydantic import ValidationError

from database import SessionLocal
from seedwork.base_consumer import BaseConsumer

from .auth import (
    get_current_active_user,
    get_current_user,
)
from .schemas import (
    AuthResponseSchema,
    AuthSchema,
    GetClientsResponseSchema,
    GetClientsSchema,
    GetSellersResponseSchema,
    GetSellersSchema,
)
from .services import get_clients_with_ids, get_sellers_with_ids


class GetSellersConsumer(BaseConsumer):
    """
    Consumer for getting sellers.
    """

    def __init__(self):
        super().__init__(queue="users.get_sellers")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all sellers.

        Args:
            data (Dict): The incoming seller ids.
        """
        db = SessionLocal()
        try:
            sellers_schema = GetSellersSchema.model_validate(payload)
            sellers = get_sellers_with_ids(db, sellers_schema.seller_ids)
            # Sort sellers by id position in payload
            if sellers_schema.seller_ids:
                sellers.sort(
                    key=lambda x: (
                        sellers_schema.seller_ids.index(x.id)
                        if x.id in sellers_schema.seller_ids
                        else -1
                    )
                )
            return GetSellersResponseSchema.model_validate(
                {"sellers": sellers}
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()


class GetClientsConsumer(BaseConsumer):
    """
    Consumer for getting clients.
    """

    def __init__(self):
        super().__init__(queue="users.get_clients")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all clients.

        Args:
            data (Dict): The incoming client ids.
        """
        db = SessionLocal()
        try:
            clients_schema = GetClientsSchema.model_validate(payload)
            clients = get_clients_with_ids(db, clients_schema.client_ids)
            # Sort clients by id position in payload
            if clients_schema.client_ids:
                clients.sort(
                    key=lambda x: (
                        clients_schema.client_ids.index(x.id)
                        if x.id in clients_schema.client_ids
                        else -1
                    )
                )
            return GetClientsResponseSchema.model_validate(
                {"clients": clients}
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()


class AuthUserConsumer(BaseConsumer):
    """
    Consumer for getting authenticated user.
    """

    def __init__(self):
        super().__init__(queue="users.auth_user")

    def process_payload(self, payload: Dict) -> str | Dict:
        """
        Consume the data and get all sellers.

        Args:
            data (Dict): The incoming seller ids.
        """
        db = SessionLocal()
        try:
            auth_schema = AuthSchema.model_validate(payload)
            user = get_current_active_user(
                current_user=get_current_user(
                    token=auth_schema.bearer_token, db=db
                )
            )
            return AuthResponseSchema.model_validate(
                {"user": user}
            ).model_dump_json()
        except ValidationError as e:
            return {"error": e.errors()}
        except HTTPException:
            return {"user": None}
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
