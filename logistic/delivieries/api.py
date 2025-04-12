from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db_dependency import get_db
from delivieries.mock_data import create_mock_delivery_detail

from . import mappers, schemas, services

deliveries_router = APIRouter(prefix="/delivery")


@deliveries_router.post("/", response_model=schemas.DeliveryCreateResponseSchema)
def create_delivery(
    delivery: schemas.DeliveryCreateRequestSchema, db: Session = Depends(get_db)
):
    pass
    #delivery = services.create_delivery(db=db, delivery=delivery)
    #return mappers.delivery_to_schema(delivery)


@deliveries_router.get("", response_model=List[schemas.DeliveryDetailResponseSchema])
@deliveries_router.get("/", response_model=List[schemas.DeliveryDetailResponseSchema])
def list_all_deliveries(
    db: Session = Depends(get_db)
):    
    return [create_mock_delivery_detail() for _ in range(10)]
