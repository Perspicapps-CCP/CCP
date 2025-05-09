from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_dependency import get_db
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient

from . import mappers, schemas, services

deliveries_router = APIRouter(prefix="/delivery")


@deliveries_router.get(
    "", response_model=List[schemas.DeliveryDetailGetResponseSchema]
)
@deliveries_router.get(
    "/", response_model=List[schemas.DeliveryDetailGetResponseSchema]
)
def list_all_deliveries(
    db: Session = Depends(get_db),
    inventory_client: InventoryClient = Depends(InventoryClient),
    suppliers_client: SuppliersClient = Depends(SuppliersClient),
):
    return mappers.deliveries_to_aggregation(
        services.get_deliveries(db),
        db,
        inventory_client,
        suppliers_client,
    )


@deliveries_router.post(
    "/", response_model=List[schemas.DeliveryCreateResponseSchema]
)
def create_delivery(
    delivery: schemas.DeliveryCreateRequestSchema,
    db: Session = Depends(get_db),
):

    delivery = services.create_delivery_transaction(db, delivery)
    return mappers.deliery_to_schema(delivery)


routes_router = APIRouter(prefix="/route")


@routes_router.get(
    "/{delivery_id}",
    response_model=List[schemas.DeliveryGetRouteSchema],
)
@routes_router.get(
    "/{delivery_id}/",
    response_model=List[schemas.DeliveryGetRouteSchema],
)
def get_delivery_route(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    inventory_client: InventoryClient = Depends(InventoryClient),
):
    warehouses_dict = {
        w.warehouse_id: w for w in inventory_client.get_warehouses()
    }

    delivery = services.get_delivery(db, delivery_id)
    if not delivery:
        return []

    warehouse = warehouses_dict.get(delivery.warehouse_id, object())

    delivery_route = services.get_delivery_route(db, delivery_id)
    return mappers.delivery_route_to_schema(
        delivery, warehouse, delivery_route
    )
