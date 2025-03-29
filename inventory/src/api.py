from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import mappers, schemas, services

deliveries_router = APIRouter(prefix="/entregas")


@deliveries_router.post("/", response_model=schemas.DeliveryDetailSchema)
def create_delivery(
    delivery: schemas.DeliveryCreateSchema, db: Session = Depends(get_db)
):
    delivery = services.create_delivery(db=db, delivery=delivery)
    return mappers.delivery_to_schema(delivery)


@deliveries_router.get(
    "/{delivery_id}", response_model=schemas.DeliveryDetailSchema
)
def delivery_detail(delivery_id: UUID, db: Session = Depends(get_db)):
    db_delivery = services.get_delivery(db, delivery_id=delivery_id)
    if db_delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )
    return mappers.delivery_to_schema(db_delivery)


@deliveries_router.get("/", response_model=List[schemas.DeliveryDetailSchema])
def list_all_deliveries(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    deliveries = services.get_deliveries(db, skip=skip, limit=limit)
    return [mappers.delivery_to_schema(delivery) for delivery in deliveries]


@deliveries_router.delete(
    "/{delivery_id}", response_model=schemas.DeleteResponse
)
def delete_delivery(delivery_id: UUID, db: Session = Depends(get_db)):
    db_delivery = services.delete_delivery(db, delivery_id=delivery_id)
    if db_delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )
    return schemas.DeleteResponse()
