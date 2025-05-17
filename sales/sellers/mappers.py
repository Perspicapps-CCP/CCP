from typing import Dict, List

from rpc_clients.users_client import UsersClient

from .models import ClientForSeller, ClientVideo, ClientVisit
from .schemas import (
    ClientForSellerDetailSchema,
    ResponseAttachmentDetailSchema,
    ResponseClientVideoSchema,
)


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


def visit_to_schema(
    visit: ClientVisit,
) -> ResponseAttachmentDetailSchema:
    return ResponseAttachmentDetailSchema(
        id=visit.id,
        client_id=visit.client_id,
        description=visit.description,
        created_at=visit.created_at,
        updated_at=visit.updated_at,
    )


def client_video_to_schema(
    client_video: ClientVideo,
) -> ResponseClientVideoSchema:
    return ResponseClientVideoSchema(
        id=client_video.id,
        title=client_video.title,
        status=client_video.status,
        description=client_video.description,
        url=client_video.url.replace(
            "gs://", "https://storage.googleapis.com/"
        ),
        recommendation=client_video.recommendations,
    )


def list_client_video_to_schema(
    list_client_videos: list[ClientVideo],
) -> list[ResponseClientVideoSchema]:
    return [
        ResponseClientVideoSchema(
            id=client_video.id,
            title=client_video.title,
            status=client_video.status,
            description=client_video.description,
            url=client_video.url.replace(
                "gs://", "https://storage.googleapis.com/"
            ),
            recommendation=client_video.recommendations,
        )
        for client_video in list_client_videos
    ]
