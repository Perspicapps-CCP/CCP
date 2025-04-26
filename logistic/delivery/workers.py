import time
import googlemaps
import logging
from celery import Celery
from datetime import timedelta
from typing import Dict, Optional
from math import radians, cos, sin, asin, sqrt

from config import CELERY_BROKER_URL, GMAPS_API_KEY
from db_dependency import get_db
from delivery import services
from delivery.services import get_delivery_address_without_geocoding
from rpc_clients.inventory_client import InventoryClient
from rpc_clients.schemas import WarehouseSchema

logger = logging.getLogger(__name__)
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,  # Limit the number of tasks fetched by each worker at a time
    task_track_started=True,  # Mark tasks as "started" when they start running
    task_reject_on_worker_lost=True,
    broker_transport_options={
        'visibility_timeout': 600
    },  # Set visibility timeout for tasks in seconds
    task_acks_late=True,  # Acknowledge tasks only after they are completed
)

celery_app.conf.beat_schedule = {
    "geocode-pending-addresses": {
        "task": "delivery.workers.geocode_pending_addresses",
        "schedule": timedelta(minutes=2),
        'options': {
            'queue': 'ccp.geocode_addresses',
            'expires': 300,  # Task expires after 5 minutes
        },
    },
    "calculate-ordered-route-stops": {
        "task": "delivery.workers.calculate_ordered_route_stops",
        "schedule": timedelta(minutes=2),  # Run every 5 minutes
        'options': {
            'queue': 'ccp.route_optimization',
            'expires': 300,  # Task expires after 10 minutes
        },
    },
}


def geocode_address(
    address_str: str, attempts: int = 3
) -> Optional[Dict[str, float]]:
    for attempt in range(attempts):
        try:
            location = gmaps.geocode(address_str)
            if location and len(location) > 0:
                lat = location[0]['geometry']['location']['lat']
                lng = location[0]['geometry']['location']['lng']
                logger.info(f"Successfully geocoded to: {lat}, {lng}")
                return {"latitude": lat, "longitude": lng}
            logger.warning(f"No results returned for '{address_str}'")
            return None
        except Exception as e:
            if attempt < attempts - 1:
                time.sleep(1)  # Wait before retrying
            else:
                logger.error(
                    f"All geocoding attempts failed for address: {address_str}"
                )
                return None


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def nearest_neighbor_route(start_point, addresses):
    """
    Creates a route using nearest neighbor algorithm
    start_point: tuple of (latitude, longitude)
    addresses: list of dicts with 'address' and 'coords' (lat, lon) keys
    """
    route = []
    unvisited = addresses.copy()
    current_point = start_point

    while unvisited:
        # Find closest unvisited address
        min_dist = float('inf')
        closest = None

        for addr in unvisited:
            dist = haversine(
                current_point[1],
                current_point[0],
                addr['coords'][1],
                addr['coords'][0],
            )
            if dist < min_dist:
                min_dist = dist
                closest = addr

        # Add to route and update current position
        route.append(closest)
        unvisited.remove(closest)
        current_point = closest['coords']

    return route


@celery_app.task(name="delivery.workers.geocode_pending_addresses")
def geocode_pending_addresses():
    db = next(get_db())

    try:
        pending_addresses = get_delivery_address_without_geocoding(db)
        logger.info(f"Found {len(pending_addresses)} addresses to geocode")

        for address in pending_addresses:
            address_str = f"{address.street}, {address.city}, {address.state}, {address.country}"
            logger.info(f"Geocoding address: {address_str}")
            result = geocode_address(address_str)

            if result:
                # Update the address with geocoded coordinates
                address.geocoding_attempts += 1
                address.latitude = result["latitude"]
                address.longitude = result["longitude"]
                logger.info(f"Successfully geocoded address ID {address.id}")
            else:
                logger.warning(f"Failed to geocode address ID {address.id}")
                address.geocoding_attempts += 1
            db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error in geocode_pending_addresses task: {str(e)}")
    finally:
        db.close()
    return {"message": "Geocoding task completed"}


@celery_app.task(name="delivery.workers.calculate_ordered_route_stops")
def calculate_ordered_route_stops():
    db = next(get_db())
    inventory_client = InventoryClient()

    try:
        warehouses_dict = {
            w.warehouse_id: w for w in inventory_client.get_warehouses()
        }

        deliveries = services.get_deliveries_without_stops_ordered(db)
        for delivery in deliveries:
            warehouse: WarehouseSchema = warehouses_dict.get(
                delivery.warehouse_id, object()
            )

            # Get the start point (warehouse location)
            start_point = (warehouse.latitude, warehouse.longitude)

            # Get the addresses from the delivery route
            addresses = [
                {
                    'stop': stop.id,
                    'coords': (stop.address.latitude, stop.address.longitude),
                }
                for stop in delivery.stops
            ]

            # Calculate the optimized route
            optimized_route = nearest_neighbor_route(start_point, addresses)

            # Save or process the optimized route as needed
            status = services.update_order_delivery_stops(db, optimized_route)
            logger.info(
                f"Optimized route for delivery {delivery.id}, status: {status}"
            )

    except Exception as e:
        logger.error(f"Error in calculate_ordered_route_stops task: {str(e)}")
