from typing import Dict, List
from uuid import UUID

from delivery import schemas


def group_items_by_warehouse(
    sale: schemas.PayloadSaleSchema,
) -> Dict[UUID, List[schemas.PayloadSaleItemSchema]]:
    """Group sale items by warehouse ID."""
    items_by_warehouse = {}
    for item in sale.sales_items:
        if item.warehouse_id not in items_by_warehouse:
            items_by_warehouse[item.warehouse_id] = []
        items_by_warehouse[item.warehouse_id].append(item)
    return items_by_warehouse


def group_stops_by_warehouse(pending_delivery_stops) -> Dict[UUID, List[UUID]]:
    """Group delivery stops by warehouse ID."""
    stops_by_warehouse = {}
    for stop_id, _, warehouse_id in pending_delivery_stops:
        if warehouse_id not in stops_by_warehouse:
            stops_by_warehouse[warehouse_id] = []
        stops_by_warehouse[warehouse_id].append(stop_id)
    return stops_by_warehouse
