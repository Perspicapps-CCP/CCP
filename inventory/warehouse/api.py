from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db_dependency import get_db

from . import mappers, schemas, services

warehouse_router = APIRouter(prefix="/warehouse")


@warehouse_router.post(
    "", response_model=schemas.WarehouseCreateResponseSchema
)
def create_warehouse(
    request: schemas.WarehouseSchema, db: Session = Depends(get_db)
):
    if services.get_warehouses(db=db, warehouse_name=request.warehouse_name):
        raise HTTPException(status_code=409, detail="Warehouse already exists")
    response = services.create_warehouse(db=db, warehouse=request)
    return mappers.warehouse_created_to_schema(response)


@warehouse_router.get(
    "", response_model=List[schemas.WarehouseGetResponseSchema]
)
def list_warehouses(
    params: schemas.FilterRequest = Depends(), db: Session = Depends(get_db)
):
    warehouses = services.get_warehouses(
        db, warehouse_id=params.id, warehouse_name=params.name
    )
    return mappers.warehouse_list_to_schema(warehouses)


@warehouse_router.get(
    "/{id}", response_model=schemas.WarehouseGetResponseSchema
)
def get_warehouse(
    params: schemas.GetRequest = Depends(), db: Session = Depends(get_db)
):
    warehouse = services.get_warehouse(db, warehouse_id=params.id)
    return mappers.warehouse_get_to_schema(warehouse)
