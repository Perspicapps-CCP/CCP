import pika

from config import BROKER_HOST


class BasePublisher:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.connection_params = pika.ConnectionParameters(
            host=BROKER_HOST,
            heartbeat=60,
            connection_attempts=3,
            retry_delay=2,
        )
        self._setup_connection()

    def _setup_connection(self):
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    def close(self):
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()
