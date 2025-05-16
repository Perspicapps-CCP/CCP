#!/bin/bash

set -e

# Start the Celery Beat scheduler in the background
echo "Starting Celery Beat scheduler..."
celery -A sellers.workers:celery_app beat --loglevel=info &
BEAT_PID=$!

# Start the Celery Worker in the background
echo "Starting Celery Worker..."
celery -A sellers.workers:celery_app worker --loglevel=info -Q ccp.video_analysis,ccp.video_recommendations &
WORKER_PID=$!

# Start the RabbitMQ consumer
python -u start_broker_consumer.py