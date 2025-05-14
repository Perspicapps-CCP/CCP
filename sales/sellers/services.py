import uuid

from sqlalchemy.orm import Session

from . import crud
from .models import (
    ClientForSeller,
    ClientVideo,
    ClientVisit,
    ClientAttachment,
)


def associate_client_with_seller(
    db: Session, seller_id: uuid.UUID, client_id: uuid.UUID
) -> ClientForSeller:
    """
    Associate a client with a seller.
    """
    if crud.does_client_for_seller_exist(db, seller_id, client_id):
        raise ValueError("Client already associated with this seller.")
    return crud.create_client_for_seller(db, seller_id, client_id)


def get_all_clients_for_seller(
    db: Session, seller_id: uuid.UUID
) -> list[ClientForSeller]:
    """
    Get all clients for a seller.
    """
    return crud.get_all_clients_for_seller(db, seller_id)


def register_client_visit(
    db: Session, client_id: uuid.UUID, description: str
) -> ClientVisit:
    """
    Register a new vist for the client.
    """
    clientVisit = ClientVisit(client_id=client_id, description=description)
    return crud.register_client_visit(db, clientVisit)


def save_client_attachment(
    db: Session, visit: uuid.UUID, pathFile: str
) -> ClientVisit:
    """
    Save attached file
    """
    clientAttachment = ClientAttachment(visit_id=visit, path_file=pathFile)
    return crud.save_client_attachment(db, clientAttachment)


def save_client_video(
    db: Session,
    client_id: uuid.UUID,
    title: str,
    description: str,
    url: str,
) -> ClientVideo:
    """
    Save video for client
    """
    clientVideo = ClientVideo(
        client_id=client_id,
        title=title,
        description=description,
        url=url,
    )
    return crud.upload_client_video(db, clientVideo)


def get_all_client_video(
    db: Session, client_id: uuid.UUID
) -> list[ClientVideo]:
    """
    Get all videos for a client.
    """
    return crud.get_all_client_video(db, client_id)


def get_all_videos_without_analysis(
    db: Session,
) -> list[ClientVideo]:
    """
    Get all videos for a client that are not analyzed.
    """
    return crud.get_all_videos_without_analysis(db)


def get_all_videos_without_recommendations(
    db: Session,
) -> list[ClientVideo]:
    """
    Get all videos for a client that are not recommended.
    """
    return crud.get_all_videos_without_recommendations(db)


def update_video_status(
    db: Session, video_id: uuid.UUID, status: str, recommendations: str = None
) -> ClientVideo:
    """
    Update the status of a video.
    """
    return crud.update_video_status(db, video_id, status, recommendations)
