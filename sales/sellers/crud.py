import uuid

from sqlalchemy.orm import Session

from .models import ClientForSeller


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
