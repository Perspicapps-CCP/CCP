import pika
import json
import threading
from abc import ABC, abstractmethod
from typing import Dict

from config import BROKER_HOST


class BaseConsumer(threading.Thread, ABC):
    def __init__(
        self, queue, durable: bool = False, auto_delete: bool = False
    ):
        threading.Thread.__init__(self)
        self.queue_name = queue
        self.connection = None
        self.channel = None
        self.durable = durable
        self.auto_delete = auto_delete

    def setup_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=BROKER_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=self.durable,
            auto_delete=self.auto_delete,
        )
        self.channel.basic_qos(prefetch_count=1)

    def run(self):
        self.setup_connection()
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback
        )
        self.channel.start_consuming()

    @abstractmethod
    def process_payload(self, payload: Dict) -> Dict: ...

    def callback(self, ch, method, props, body):
        print(f" [x] Received {body}")
        json_body = json.loads(body) if body else {}
        response = self.process_payload(json_body)
        if props.reply_to:
            ch.basic_publish(
                exchange="",
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=props.correlation_id
                ),
                body=(
                    json.dumps(response)
                    if isinstance(response, dict)
                    else response
                ),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def stop(self):
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()
