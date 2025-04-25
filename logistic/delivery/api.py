from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_dependency import get_db
from delivery.mappers import delivery_route_to_schema
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.suppliers_client import SuppliersClient
from . import schemas, services

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

    warehouses_dict = {
        w.warehouse_id: w for w in inventory_client.get_warehouses()
    }
    products_dict = {p.id: p for p in suppliers_client.get_all_products()}

    deliveries_aggregated: List[schemas.DeliveryDetailGetResponseSchema] = []
    for delivery in services.get_deliveries(db):
        delivery_agg = schemas.DeliveryDetailGetResponseSchema(
            shipping_number=str(delivery.id),
            license_plate=delivery.driver.license_plate,
            diver_name=delivery.driver.name,
            warehouse=schemas.WarehouseSchema(
                warehouse_id=delivery.warehouse_id,
                warehouse_name=getattr(
                    warehouses_dict.get(delivery.warehouse_id, object()),
                    "warehouse_name",
                    "Unknown Warehouse",
                ),
            ),
            delivery_status=delivery.status,
            created_at=delivery.created_at,
            updated_at=delivery.updated_at,
            orders=[],
        )

        for item, address in services.get_delivery_items(db, delivery.id):
            delivery_item = schemas.DeliveryItemGetResponseSchema(
                order_number=str(item.sales_id),
                order_address=address,
                product_code=getattr(
                    products_dict.get(item.product_id, object()),
                    "product_code",
                    "Unknown Code",
                ),
                product_name=getattr(
                    products_dict.get(item.product_id, object()),
                    "name",
                    "Unknown Product",
                ),
                images=getattr(
                    products_dict.get(item.product_id, object()), "images", []
                ),
            )
            delivery_agg.orders.append(delivery_item)

        deliveries_aggregated.append(delivery_agg)
    return deliveries_aggregated


@deliveries_router.post(
    "/", response_model=schemas.DeliveryCreateResponseSchema
)
def create_delivery(
    delivery: schemas.DeliveryCreateRequestSchema,
    db: Session = Depends(get_db),
):
    # delivery = services.create_delivery(db=db, delivery=delivery)
    # return mappers.delivery_to_schema(delivery)
    pass


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
    return delivery_route_to_schema(delivery, warehouse, delivery_route)
