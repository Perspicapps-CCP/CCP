import logging
import threading
import time

import keyboard

from delivery.consumers import (
    CreateDeliveryStopsConsumer,
    GetDeliveriesConsumer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

threads = []


def run_thread(threaded_class: type[threading.Thread], num_errors=0):
    try:
        thread = threaded_class()
        threads.append(thread)
        thread.start()
    except Exception as e:
        logger.error(f"Error running thread {threaded_class.__name__}: {e}")
        if num_errors < 3:
            run_thread(threaded_class, num_errors + 1)


def start_threads(threaded_classes: list):
    for threaded_class in threaded_classes:
        run_thread(threaded_class)


start_threads([CreateDeliveryStopsConsumer, GetDeliveriesConsumer])


try:
    logger.info("Starting consumer threads...")
    while any(t.is_alive() for t in threads) and not keyboard.is_pressed('q'):
        time.sleep(1)
except KeyboardInterrupt:
    logger.error("Keyboard interrupt received, shutting down...")
    for thread in threads:
        if hasattr(thread, 'stop') and callable(thread.stop):
            thread.stop()
logger.info("All consumers stopped, exiting...")
