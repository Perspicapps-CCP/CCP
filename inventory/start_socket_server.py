from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import logging
import os

import config
from stock.websocket import sio_app
from stock.consumers import _stockChangesConsumer


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def health_check(request):
    """Simple health check endpoint to verify service status"""
    return JSONResponse(
        {"status": "ok", "service": "inventory-socket-service"}
    )


async def on_startup():
    """Startup event handler that initializes and starts the RabbitMQ consumer"""
    logger.info("Application starting up...")

    try:
        logger.info("Initializing RabbitMQ consumer...")
        _stockChangesConsumer.setup_connection()
        _stockChangesConsumer.start()
        logger.info("RabbitMQ consumer started successfully")
    except Exception as e:
        logger.error(f"Error starting RabbitMQ consumer: {str(e)}")


async def on_shutdown():
    """Shutdown event handler that gracefully stops the RabbitMQ consumer"""
    logger.info("Application shutting down...")

    try:
        logger.info("Stopping RabbitMQ consumer...")
        _stockChangesConsumer.stop()
        logger.info("RabbitMQ consumer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping RabbitMQ consumer: {str(e)}")


routes = [
    Route("/inventory/health", endpoint=health_check, methods=["GET"]),
    Mount("/inventory/ws", app=sio_app),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
]


app = Starlette(
    debug=os.getenv("DEBUG", "false").lower() == "true",
    routes=routes,
    middleware=middleware,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)
