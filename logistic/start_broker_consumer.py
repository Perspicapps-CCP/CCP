import threading

from delivieries.consumer import CreateDeliveryConsumer


def run_thread(threaded_class: type[threading.Thread], num_errors=0):
    try:
        threaded_class().start()
    except Exception as e:
        print(f"Error running thread {threaded_class.__name__}: {e}")
        if num_errors < 3:
            run_thread(threaded_class, num_errors + 1)


def start_threads(threaded_classes: list):
    for threaded_class in threaded_classes:
        run_thread(threaded_class)


start_threads([CreateDeliveryConsumer])
