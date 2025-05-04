import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

from stock import websocket


@pytest.fixture
def reset_clients():
    websocket.clients = {}
    yield
    websocket.clients = {}


@pytest_asyncio.fixture
def mock_sio():
    with patch.object(websocket, 'sio') as mock_sio:
        mock_sio.enter_room = AsyncMock()
        mock_sio.leave_room = AsyncMock()
        mock_sio.emit = AsyncMock()
        yield mock_sio


@pytest.mark.asyncio
async def test_connect(reset_clients):
    sid = "test_sid"
    environ = {}

    await websocket.connect(sid, environ)

    assert sid in websocket.clients
    assert websocket.clients[sid]["rooms"] == set()


@pytest.mark.asyncio
async def test_disconnect(reset_clients):
    sid = "test_sid"
    websocket.clients[sid] = {"rooms": set()}

    await websocket.disconnect(sid)

    assert sid not in websocket.clients


@pytest.mark.asyncio
async def test_subscribe_to_product(reset_clients, mock_sio):
    sid = "test_sid"
    product_id = "123"
    data = {"product_id": product_id}
    websocket.clients[sid] = {"rooms": set()}

    await websocket.subscribe_to_product(sid, data)

    mock_sio.enter_room.assert_called_once_with(sid, f"product_{product_id}")
    assert f"product_{product_id}" in websocket.clients[sid]["rooms"]
    mock_sio.emit.assert_called_once_with(
        'subscription_confirmed', {'product_id': product_id}, room=sid
    )


@pytest.mark.asyncio
async def test_subscribe_to_product_missing_id(reset_clients, mock_sio):
    sid = "test_sid"
    data = {}  # No product_id
    websocket.clients[sid] = {"rooms": set()}

    await websocket.subscribe_to_product(sid, data)

    mock_sio.enter_room.assert_not_called()
    assert len(websocket.clients[sid]["rooms"]) == 0
    mock_sio.emit.assert_not_called()


@pytest.mark.asyncio
async def test_unsubscribe_from_product(reset_clients, mock_sio):
    sid = "test_sid"
    product_id = "123"
    data = {"product_id": product_id}
    room = f"product_{product_id}"
    websocket.clients[sid] = {"rooms": {room}}

    await websocket.unsubscribe_from_product(sid, data)

    mock_sio.leave_room.assert_called_once_with(sid, room)
    assert room not in websocket.clients[sid]["rooms"]


@pytest.mark.asyncio
async def test_unsubscribe_from_product_missing_id(reset_clients, mock_sio):
    sid = "test_sid"
    data = {}  # No product_id
    websocket.clients[sid] = {"rooms": {"some_room"}}

    await websocket.unsubscribe_from_product(sid, data)

    mock_sio.leave_room.assert_not_called()
    assert len(websocket.clients[sid]["rooms"]) == 1


@pytest.mark.asyncio
async def test_subscribe_to_all_products(reset_clients, mock_sio):
    sid = "test_sid"
    websocket.clients[sid] = {"rooms": set()}

    await websocket.subscribe_to_all_products(sid)

    mock_sio.enter_room.assert_called_once_with(sid, "all_products")
    assert "all_products" in websocket.clients[sid]["rooms"]
    mock_sio.emit.assert_called_once_with(
        'all_products_subscription_confirmed', room=sid
    )


@pytest.mark.asyncio
async def test_unsubscribe_from_all_products(reset_clients, mock_sio):
    sid = "test_sid"
    room = "all_products"
    websocket.clients[sid] = {"rooms": {room}}

    await websocket.unsubscribe_from_all_products(sid)

    mock_sio.leave_room.assert_called_once_with(sid, room)
    assert room not in websocket.clients[sid]["rooms"]


@pytest.mark.asyncio
async def test_broadcast_inventory_update(mock_sio):
    product_id = "123"
    update_data = {"product_id": product_id, "quantity": 10}

    await websocket.broadcast_inventory_update(product_id, update_data)

    assert mock_sio.emit.call_count == 2
    mock_sio.emit.assert_any_call(
        'inventory_change', update_data, room=f"product_{product_id}"
    )
    mock_sio.emit.assert_any_call(
        'inventory_change', update_data, room='all_products'
    )
