import uuid

from sqlalchemy.orm import Session

from .models import (
    ClientForSeller,
    ClientVideo,
    ClientVisit,
    ClientAttachment,
    VideoStatusEnum,
)
from datetime import datetime


def _basee_query(
    db: Session,
) -> ClientForSeller:
    """
    Base query for the ClientForSeller model.
    """
    return db.query(ClientForSeller)


def create_client_for_seller(
    db: Session,
    seller_id: uuid.UUID,
    client_id: uuid.UUID,
) -> ClientForSeller:
    """
    Create a new client for a seller.
    """
    client_for_seller = ClientForSeller(
        client_id=client_id,
        seller_id=seller_id,
    )
    db.add(client_for_seller)
    db.commit()
    return client_for_seller


def does_client_for_seller_exist(
    db: Session,
    seller_id: uuid.UUID,
    client_id: uuid.UUID,
) -> bool:
    """
    Check if a client for a seller exists.
    """
    return (
        _basee_query(db)
        .filter(
            ClientForSeller.seller_id == seller_id,
            ClientForSeller.client_id == client_id,
        )
        .first()
        is not None
    )


def get_all_clients_for_seller(
    db: Session,
    seller_id: uuid.UUID = None,
) -> list[ClientForSeller]:
    """
    Get all clients for a seller.
    """
    qs = _basee_query(db)
    if seller_id:
        qs = qs.filter(ClientForSeller.seller_id == seller_id)
    return qs.order_by(ClientForSeller.created_at.desc()).all()


def register_client_visit(
    db: Session,
    visit: ClientVisit,
) -> ClientVisit:
    """
    Create a new visit for a client and update last_visited field.
    """
    db.add(visit)
    db.commit()

    query = _basee_query(db)
    client_for_seller = query.filter(
        ClientForSeller.client_id == visit.client_id
    ).first()

    if client_for_seller:
        client_for_seller.last_visited = datetime.datetime.utcnow()
        db.commit()

    return visit


def save_client_attachment(
    db: Session,
    clientAttachment: ClientAttachment,
) -> ClientAttachment:
    """
    Save the attached file for the client.
    """
    db.add(clientAttachment)
    db.commit()

    return clientAttachment


def upload_client_video(
    db: Session,
    clientVideo: ClientVideo,
) -> ClientVideo:
    """
    Save the attached file for the client.
    """
    db.add(clientVideo)
    db.commit()

    return clientVideo


def get_all_client_video(
    db: Session,
    client_id: uuid.UUID,
) -> list[ClientVideo]:
    """
    Get all videos for a client.
    """
    return (
        db.query(ClientVideo).filter(ClientVideo.client_id == client_id).all()
    )


def get_all_videos_without_analysis(
    db: Session,
) -> list[ClientVideo]:
    """
    Get all videos for a client that are not analyzed.
    """
    return (
        db.query(ClientVideo)
        .filter(
            ClientVideo.status == VideoStatusEnum.PENDING,
        )
        .all()
    )


def get_all_videos_without_recommendations(
    db: Session,
) -> list[ClientVideo]:
    """
    Get all videos for a client that are not analyzed.
    """
    return (
        db.query(ClientVideo)
        .filter(
            ClientVideo.status == VideoStatusEnum.ANALISYS_GENERATED,
        )
        .all()
    )


def update_video_status(
    db: Session,
    video_id: uuid.UUID,
    status: VideoStatusEnum,
    recommendations: str = None,
) -> ClientVideo:
    """
    Update the status of a video.
    """
    video = db.query(ClientVideo).filter(ClientVideo.id == video_id).first()
    if not video:
        return None

    video.status = status
    if recommendations:
        video.recommendations = recommendations

    db.commit()
    db.refresh(video)
    return video
