import threading
import asyncio
from typing import Dict
from seedwork.base_consumer import BaseConsumer
from stock.websocket import broadcast_inventory_update


class GetStocksEventsConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(queue="", auto_delete=True, durable=True)
        self.should_stop = False
        self.consumer_thread = None
        self.exchange_name = "inventory_events"
        self.exchange_type = "fanout"
        self.exclusive = True
        self.loop = asyncio.new_event_loop()

    def setup_connection(self):
        super().setup_connection()

        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=self.exchange_type,
            durable=self.durable,
        )

        # Cola exclusiva para este consumidor
        result = self.channel.queue_declare(queue='', exclusive=self.exclusive)
        self.queue_name = result.method.queue

        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=self.queue_name,
        )

        # Configurar el callback de consumo
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
            auto_ack=True,
        )

        return self

    def process_payload(self, payload: Dict) -> None:
        """Callback cuando se recibe un mensaje"""
        try:
            print(
                f"Enviando mensaje al sockets. Accion: {payload.get('action')}"
            )
            asyncio.run_coroutine_threadsafe(
                broadcast_inventory_update(
                    payload.get('data')["product_id"], payload.get('data')
                ),
                self.loop,
            )
            print("Enviando completado..!!")

        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")

    def start(self):

        def run_event_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        loop_thread = threading.Thread(target=run_event_loop, daemon=True)
        loop_thread.start()

        def consume_loop():
            try:
                print("Iniciando consumo de mensajes RabbitMQ...")
                self.channel.start_consuming()
            except Exception as e:
                print(f"Error en el consumo de mensajes: {str(e)}")
            finally:
                if not self.should_stop:
                    # Reintentar conexión si no fue una parada deliberada
                    self.setup_connection()
                    self.start()

        self.consumer_thread = threading.Thread(
            target=consume_loop, daemon=True
        )
        self.consumer_thread.start()

    def stop(self):
        self.should_stop = True
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        self.loop.call_soon_threadsafe(self.loop.stop)


_stockChangesConsumer = GetStocksEventsConsumer()
