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
