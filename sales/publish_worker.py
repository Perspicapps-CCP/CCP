import logging
from celery import Celery
from datetime import timedelta

from config import BROKER_HOST
from db_dependency import get_db
from rpc_clients.logistic_client import LogisticClient
from rpc_clients.schemas import PayloadSaleSchema
from sales.models import OutboxStatus
from sales.services import get_pending_sales, add_new_sales_to_outbox, set_status_outbox_item


logger = logging.getLogger(__name__)

celery_app = Celery("publish_sales_tasks", broker=f"pyamqp://guest:guest@{BROKER_HOST}:5672/")

celery_app.conf.update(
    task_acks_late=True,  # Tasks are acknowledged after execution
    task_reject_on_worker_lost=True,  # Tasks are rejected if worker disconnects
    task_default_queue='task.sales',
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_track_started=True,  # Mark tasks as "started" when they start running
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "send-pending-sales-logistics": {
        "task": "publish_worker.send_orders_to_logistics",
        "schedule": timedelta(minutes=2),
        'options': {
            'queue': 'task.sales',
            'expires': 300,  # Task expires after 5 minutes
        },
    },
}


@celery_app.task
def send_orders_to_logistics() -> str:
    db = next(get_db())
    logistic_client = LogisticClient()
    try:
        logger.info("Starting to process pending sales")
        add_new_sales_to_outbox(db)
        sales_list = get_pending_sales(db)

        if not sales_list:
            logger.info("No pending sales orders to send.")
            return "No pending sales orders to send."

        for sale in sales_list:
            try:
                result = logistic_client.send_pending_sales_orders_to_logistics(
                        PayloadSaleSchema.model_validate_json(sale.get_payload())
                    )

                if result:
                    set_status_outbox_item(db, sale.id, OutboxStatus.SENT)
                else:
                    set_status_outbox_item(db, sale.id, OutboxStatus.FAILED)

            except Exception as e:
                logger.error(f"Failed to send sale order {sale.id}: {e}")
                set_status_outbox_item(db, sale.id, OutboxStatus.FAILED, str(e))
                continue
        message = (
            f"Processed orders to logistics: {len(sales_list)} sales orders."
        )
        logger.info(message)
        return message
    except Exception as e:
        logger.error(f"Failed to get pending sales list: {e}")
        return f"Failed to get pending sales list: {e}"
    finally:
        db.close()
