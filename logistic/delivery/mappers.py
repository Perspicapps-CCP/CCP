from typing import List, Tuple

from delivery import models, schemas
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.schemas import WarehouseSchema
from rpc_clients.suppliers_client import SuppliersClient


def delivery_route_to_schema(
    delivery: models.Delivery,
    warehouse: WarehouseSchema,
    delivery_route: List[
        Tuple[models.Delivery, models.DeliveryStop, models.DeliveryAddress]
    ],
) -> List[schemas.DeliveryGetRouteSchema]:
    route_stops = []
    route_stops.append(
        schemas.DeliveryGetRouteSchema(
            shipping_number=delivery.id,
            order_number=0,
            order_address=warehouse.address,
            order_customer_name=warehouse.warehouse_name,
            latitude=warehouse.latitude,
            longitude=warehouse.longitude,
        )
    )

    for delivery, stop, address in delivery_route:
        route_stops.append(
            schemas.DeliveryGetRouteSchema(
                shipping_number=str(delivery.id),
                order_number=str(stop.order_number),
                order_address=f"{address.street} {address.city}",
                latitude=address.latitude,
                longitude=address.longitude,
            )
        )
    return route_stops


def deliery_to_schema(
    deliveries: List[models.Delivery],
) -> List[schemas.DeliveryCreateResponseSchema]:
    """Convert a delivery to a schema."""

    deliveries_aggregated = []
    for delivery in deliveries:
        deliveries_aggregated.append(
            schemas.DeliveryCreateResponseSchema(
                shipping_number=str(delivery.id),
                diver_name=delivery.driver.name,
                license_plate=delivery.driver.license_plate,
                warehouse=schemas.WarehouseSchema(
                    warehouse_id=delivery.warehouse_id,
                    warehouse_name="Unknown Warehouse",
                ),
                delivery_status=delivery.status,
                created_at=delivery.created_at,
                updated_at=delivery.updated_at,
            )
        )

    return deliveries_aggregated


def deliveries_to_aggregation(
    deliveries: List[models.Delivery],
    db,
    inventory_client: InventoryClient,
    suppliers_client: SuppliersClient,
) -> List[schemas.DeliveryDetailGetResponseSchema]:
    from .services import get_delivery_items

    warehouses_dict = {
        w.warehouse_id: w for w in inventory_client.get_warehouses()
    }
    products_dict = {p.id: p for p in suppliers_client.get_all_products()}

    deliveries_aggregated: List[schemas.DeliveryDetailGetResponseSchema] = []
    for delivery in deliveries:
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

        for item, address in get_delivery_items(db, delivery.id):
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
