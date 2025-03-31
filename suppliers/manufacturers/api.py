from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import mappers, schemas, services

manufacturers_router = APIRouter(prefix="/manufacturers")


@manufacturers_router.post(
    "/", response_model=schemas.ManufacturerDetailSchema
)
def create_manufacturer(
    manufacturer: schemas.ManufacturerCreateSchema,
    db: Session = Depends(get_db),
):
    if services.get_manufacturer_by_id_type(db=db, manufacturer=manufacturer):
        raise HTTPException(
            status_code=409, detail="Manufacturer already exists"
        )
    manufacturer = services.create_manufacturer(
        db=db, manufacturer=manufacturer
    )
    return mappers.manufacturer_to_schema(manufacturer)


@manufacturers_router.get(
    "/{manufacturer_id}", response_model=schemas.ManufacturerDetailSchema
)
def manufacturer_detail(manufacturer_id: UUID, db: Session = Depends(get_db)):
    db_manufacturer = services.get_manufacturer(
        db, manufacturer_id=manufacturer_id
    )
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return mappers.manufacturer_to_schema(db_manufacturer)


@manufacturers_router.get(
    "/", response_model=List[schemas.ManufacturerDetailSchema]
)
def list_all_manufacturers(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    manufacturers = services.get_manufacturers(db, skip=skip, limit=limit)
    return [
        mappers.manufacturer_to_schema(manufacturer)
        for manufacturer in manufacturers
    ]
