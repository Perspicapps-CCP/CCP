#!/bin/bash

set -e

# Start the Celery Beat scheduler in the background
echo "Starting Celery Beat scheduler..."
celery -A delivery.workers.celery_app beat --loglevel=info &
BEAT_PID=$!

# Start the Celery Worker in the background
echo "Starting Celery Worker..."
celery -A delivery.workers.celery_app worker --loglevel=info -Q ccp.geocode_addresses,ccp.route_optimization &
WORKER_PID=$!

# Start the RabbitMQ consumer
python -u start_broker_consumer.py