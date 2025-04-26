from typing import Dict, List

from rpc_clients.users_client import UsersClient

from .models import ClientForSeller
from .schemas import ClientForSellerDetailSchema


def _client_for_seller_to_schema(
    client_for_seller: ClientForSeller, clients: Dict
) -> ClientForSellerDetailSchema:
    """
    Convert a ClientForSeller object to a ClientForSellerDetailSchema object.
    """
    return ClientForSellerDetailSchema(
        id=client_for_seller.id,
        client=clients[client_for_seller.client_id],
        created_at=client_for_seller.created_at,
        updated_at=client_for_seller.updated_at,
        last_visited=client_for_seller.last_visited,
        was_visited_recently=client_for_seller.was_visited_recently,
    )


def client_for_seller_to_schema(
    client_for_seller: ClientForSeller,
) -> ClientForSellerDetailSchema:
    """
    Convert a ClientForSeller object to a ClientForSellerDetailSchema object.
    """
    return clients_for_sellers_to_schema([client_for_seller])[0]


def clients_for_sellers_to_schema(
    clients_for_sellers: List[ClientForSeller],
) -> List[ClientForSellerDetailSchema]:
    """
    Convert a list of ClientForSeller objects to a list of ClientForSellerDetailSchema objects.
    """
    # Get all client IDs and seller IDs from the entities
    client_ids = {cfs.client_id for cfs in clients_for_sellers}

    # Fetch clients and sellers in bulk
    clients = {c.id: c for c in UsersClient().get_clients(client_ids)}

    # Map each ClientForSeller to its schema
    result = []
    for client_for_seller in clients_for_sellers:
        result.append(
            _client_for_seller_to_schema(
                client_for_seller=client_for_seller,
                clients=clients,
            )
        )
    return result
