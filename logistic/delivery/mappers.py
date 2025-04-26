from typing import List, Tuple

from delivery import models, schemas
from rpc_clients.schemas import WarehouseSchema


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
