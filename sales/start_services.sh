#!/bin/bash

# Start the Celery Beat scheduler in the background
celery -A publish_worker.celery_app beat --loglevel=info &

# Start the Celery Worker in the background
celery -A publish_worker.celery_app worker --loglevel=info 

# Start the RabbitMQ consumer
# python -u start_broker_consumer.py