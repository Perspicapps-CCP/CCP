import socketio
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(asctime)s - %(name)s - %(message)s',
)

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["*", "http://127.0.0.1:5500"],
    transports=["websocket", "polling"],
)

sio_app = socketio.ASGIApp(sio, socketio_path="")

clients = {}


@sio.event
async def connect(sid, environ):
    """Handle new client connections"""
    logger.info(f"Client connected: {sid}")
    clients[sid] = {"rooms": set()}


@sio.event
async def disconnect(sid):
    """Handle client disconnections"""
    logger.info(f"Client disconnected: {sid}")
    if sid in clients:
        del clients[sid]


@sio.event
async def subscribe_to_product(sid, data):
    """Subscribe client to updates for a specific product"""
    if 'product_id' not in data:
        return

    product_id = data['product_id']
    room = f"product_{product_id}"

    await sio.enter_room(sid, room)

    if sid in clients:
        clients[sid]["rooms"].add(room)

    logger.info(f"Client {sid} subscribed to product {product_id}")

    await sio.emit(
        'subscription_confirmed', {'product_id': product_id}, room=sid
    )


@sio.event
async def unsubscribe_from_product(sid, data):
    """Unsubscribe client from updates for a specific product"""
    if 'product_id' not in data:
        return

    product_id = data['product_id']
    room = f"product_{product_id}"

    await sio.leave_room(sid, room)

    if sid in clients and room in clients[sid]["rooms"]:
        clients[sid]["rooms"].remove(room)

    logger.info(f"Client {sid} unsubscribed from product {product_id}")


@sio.event
async def subscribe_to_all_products(sid):
    """Subscribe client to all product updates"""
    room = "all_products"

    await sio.enter_room(sid, room)

    if sid in clients:
        clients[sid]["rooms"].add(room)

    logger.info(f"Client {sid} subscribed to all product updates")

    await sio.emit('all_products_subscription_confirmed', room=sid)


@sio.event
async def unsubscribe_from_all_products(sid):
    """Unsubscribe client from all product updates"""
    room = "all_products"

    await sio.leave_room(sid, room)

    if sid in clients and room in clients[sid]["rooms"]:
        clients[sid]["rooms"].remove(room)

    logger.info(f"Client {sid} unsubscribed from all product updates")


async def broadcast_inventory_update(product_id, update_data):
    """Send product update to all subscribers of a specific product"""
    room = f"product_{product_id}"

    await sio.emit('inventory_change', update_data, room=room)

    await sio.emit('inventory_change', update_data, room='all_products')
