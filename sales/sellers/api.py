from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.orm import Session

from common.api import get_auth_seller
from db_dependency import get_db
from uuid import UUID

from . import mappers, schemas, services

sellers_router = APIRouter(prefix="/sellers")


@sellers_router.post(
    "/clients",
    response_model=schemas.ClientForSellerDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": schemas.ErrorResponseSchema,
            "description": "Bad Request",
        }
    },
)
def associate_client(
    payload: Dict,
    db: Session = Depends(get_db),
    seller=Depends(get_auth_seller),
) -> schemas.ClientForSellerDetailSchema:
    """
    Create a new sales plan.
    """
    try:
        payload = schemas.ClientForSellerCreateSchema.model_validate(
            payload, context={"db": db, "seller": seller}
        )
        client_for_seller = services.associate_client_with_seller(
            db, seller.id, payload.client_id
        )
        return mappers.client_for_seller_to_schema(client_for_seller)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Timeout error, please try again in a few minutes.",
        )


@sellers_router.get(
    "/clients",
    response_model=List[schemas.ClientForSellerDetailSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "List of all client-seller associations.",
        }
    },
)
def list_clients_for_sellers(
    db: Session = Depends(get_db),
    seller=Depends(get_auth_seller),
) -> List[schemas.ClientForSellerDetailSchema]:
    """
    List all client-seller associations.
    """
    clients_for_sellers = services.get_all_clients_for_seller(db, seller.id)
    return mappers.clients_for_sellers_to_schema(clients_for_sellers)


@sellers_router.post(
    "/clients/{client_id}/visit",
    response_model=schemas.RegisterClientVisitDetailSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": schemas.ErrorResponseSchema,
            "description": "Bad Request",
        }
    },
)
def register_client_visit(
    client_id: UUID,
    payload: schemas.RegisterClientVisitSchema,
    db: Session = Depends(get_db),
) -> schemas.RegisterClientVisitDetailSchema:
    """
    Register a new client visit.
    """
    try:
        visit = services.register_client_visit(
            db=db, client_id=client_id, visit=payload
        )
        print(visit.client_id)
        return mappers.visit_to_schema(visit)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(e.errors()),
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Timeout error, please try again in a few minutes.",
        )
