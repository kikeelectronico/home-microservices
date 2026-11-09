import signal
import logging
import threading

_stop_event = threading.Event()

def handle_shutdown(signum, frame):
    logging.info("Shutdown signal received.")
    logging.info("Shutdown process initiated.")
    _stop_event.set()

def register_shutdown_handlers():
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

def stop_requested() -> bool:
    return _stop_event.is_set()

def wait_for_stop(timeout: float) -> bool:
    return _stop_event.wait(timeout)