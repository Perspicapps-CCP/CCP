import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_env_and_gmaps(monkeypatch):
    monkeypatch.setenv("GMAPS_API_KEY", "fake-key")

    mock_client = MagicMock()
    mock_client.geocode.return_value = [{
        'geometry': {'location': {'lat': 1.23, 'lng': 4.56}}
    }]

    with patch("googlemaps.Client", return_value=mock_client):
        yield

def test_geocode_address_success():
    from delivery import workers
    result = workers.geocode_address("Fake Address")
    assert result == {"latitude": 1.23, "longitude": 4.56}


def test_geocode_address_failure():
    from delivery import workers
    with patch.object(workers.gmaps, 'geocode', side_effect=Exception("Boom")):
        result = workers.geocode_address("Bad Address", attempts=1)
        assert result is None

def test_haversine_distance():
    from delivery import workers
    dist = workers.haversine(-73.9857, 40.7484, -0.1278, 51.5074)
    assert round(dist) in range(5540, 5600)

def test_nearest_neighbor_route():
    from delivery import workers
    start = (0.0, 0.0)
    addresses = [
        {'address': 'A', 'coords': (0.0, 1.0)},
        {'address': 'B', 'coords': (1.0, 0.0)},
    ]
    route = workers.nearest_neighbor_route(start, addresses)
    assert len(route) == 2
    assert all('coords' in stop for stop in route)


@patch("delivery.workers.get_db")
@patch("delivery.workers.get_delivery_address_without_geocoding")
@patch("delivery.workers.geocode_address")
def test_geocode_pending_addresses_success(mock_geocode, mock_get_addresses, mock_get_db):
    from delivery import workers

    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    mock_address = MagicMock()
    mock_address.street = "Calle Falsa"
    mock_address.city = "Ciudad"
    mock_address.state = "Provincia"
    mock_address.country = "País"
    mock_address.id = 123
    mock_address.geocoding_attempts = 0

    mock_get_addresses.return_value = [mock_address]
    mock_geocode.return_value = {"latitude": 10.0, "longitude": 20.0}

    result = workers.geocode_pending_addresses()

    assert result == {"message": "Geocoding task completed"}
    assert mock_address.latitude == 10.0
    assert mock_address.longitude == 20.0
    assert mock_db.commit.called

@patch("delivery.workers.get_db")
@patch("delivery.workers.InventoryClient")
@patch("delivery.workers.services.get_deliveries_without_stops_ordered")
@patch("delivery.workers.services.update_order_delivery_stops")
def test_calculate_ordered_route_stops_success(
    mock_update,
    mock_get_deliveries,
    mock_inventory_client,
    mock_get_db
):
    from delivery import workers

    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    mock_warehouse = MagicMock()
    mock_warehouse.warehouse_id = 1
    mock_warehouse.latitude = 0.0
    mock_warehouse.longitude = 0.0
    mock_inventory_client.return_value.get_warehouses.return_value = [mock_warehouse]

    mock_stop = MagicMock()
    mock_stop.id = 1
    mock_stop.address.latitude = 1.0
    mock_stop.address.longitude = 1.0

    mock_delivery = MagicMock()
    mock_delivery.id = 99
    mock_delivery.warehouse_id = 1
    mock_delivery.stops = [mock_stop]

    mock_get_deliveries.return_value = [mock_delivery]
    mock_update.return_value = "OK"

    workers.calculate_ordered_route_stops()

    mock_update.assert_called_once()

@patch("delivery.workers.get_db")
@patch("delivery.workers.get_delivery_address_without_geocoding")
@patch("delivery.workers.geocode_address")
def test_geocode_pending_addresses_db_error(mock_geocode, mock_get_addresses, mock_get_db):
    from delivery import workers

    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    mock_address = MagicMock()
    mock_address.id = 123
    mock_get_addresses.return_value = [mock_address]
    mock_geocode.return_value = {"latitude": 10.0, "longitude": 20.0}

    mock_db.commit.side_effect = Exception("DB Commit Error")

    result = workers.geocode_pending_addresses()

    assert result == {"message": "Geocoding task completed"}
    assert mock_db.rollback.called


@patch("delivery.workers.get_db")
@patch("delivery.workers.InventoryClient")
@patch("delivery.workers.services.get_deliveries_without_stops_ordered")
@patch("delivery.workers.services.update_order_delivery_stops")
def test_calculate_ordered_route_stops_service_error(
    mock_update,
    mock_get_deliveries,
    mock_inventory_client,
    mock_get_db
):
    from delivery import workers

    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    mock_warehouse = MagicMock()
    mock_warehouse.warehouse_id = 1
    mock_warehouse.latitude = 0.0
    mock_warehouse.longitude = 0.0
    mock_inventory_client.return_value.get_warehouses.return_value = [mock_warehouse]

    mock_stop = MagicMock()
    mock_stop.id = 1
    mock_stop.address.latitude = 1.0
    mock_stop.address.longitude = 1.0

    mock_delivery = MagicMock()
    mock_delivery.id = 99
    mock_delivery.warehouse_id = 1
    mock_delivery.stops = [mock_stop]

    mock_get_deliveries.return_value = [mock_delivery]

    mock_update.side_effect = Exception("Service Error")

    workers.calculate_ordered_route_stops()

    assert mock_update.called


@patch("delivery.workers.get_db")
@patch("delivery.workers.InventoryClient")
@patch("delivery.workers.services.get_deliveries_without_stops_ordered")
@patch("delivery.workers.services.update_order_delivery_stops")
def test_calculate_ordered_route_stops_full_interaction(
    mock_update,
    mock_get_deliveries,
    mock_inventory_client,
    mock_get_db
):
    from delivery import workers

    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])

    mock_warehouse = MagicMock()
    mock_warehouse.warehouse_id = 1
    mock_warehouse.latitude = 0.0
    mock_warehouse.longitude = 0.0
    mock_inventory_client.return_value.get_warehouses.return_value = [mock_warehouse]

    mock_stop = MagicMock()
    mock_stop.id = 1
    mock_stop.address.latitude = 1.0
    mock_stop.address.longitude = 1.0

    mock_delivery = MagicMock()
    mock_delivery.id = 99
    mock_delivery.warehouse_id = 1
    mock_delivery.stops = [mock_stop]

    mock_get_deliveries.return_value = [mock_delivery]
    mock_update.return_value = "OK"

    workers.calculate_ordered_route_stops()

    mock_update.assert_called_once()




