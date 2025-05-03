import uuid

from sqlalchemy.orm import Session

from . import crud
from .models import ClientForSeller, ClientVisit, ClientAttachment
from .schemas import RegisterClientVisitSchema


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
