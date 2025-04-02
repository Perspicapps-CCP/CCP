import json
import threading
from abc import ABC, abstractmethod
from typing import Dict

import pika

from config import BROKER_HOST


class BaseConsumer(threading.Thread, ABC):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=BROKER_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=self.queue, on_message_callback=self.callback
        )
        channel.start_consuming()

    @abstractmethod
    def process_payload(self, payload: Dict) -> Dict: ...

    def callback(self, ch, method, props, body):
        print(f" [x] Received {body}")
        json_body = json.loads(body)
        response = self.process_payload(json_body)
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
