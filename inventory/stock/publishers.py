import logging
import pika

from seedwork.base_publisher import BasePublisher
from stock import schemas

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)


def get_rabbitmq_connection():
    """Return a new RabbitMQ publisher connection"""
    return BasePublisher()


def publish_stock_change(data: schemas.EventSchema):
    publisher = None
    try:
        """Publicar cambios en el inventario a RabbitMQ"""
        publisher = get_rabbitmq_connection()

        # Asegurar que existe el exchange
        publisher.channel.exchange_declare(
            exchange="inventory_events", exchange_type="fanout", durable=True
        )

        # Publicar mensaje
        publisher.channel.basic_publish(
            exchange="inventory_events",
            routing_key="",
            body=data.model_dump_json(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # mensaje persistente
                content_type="application/json",
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        pass
    finally:
        if publisher:
            try:
                publisher.close()
            except Exception as close_error:
                logger.warning(f"Error closing connection: {close_error}")
