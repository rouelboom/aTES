"""
Provides tool publishing messages to rabbitmq
"""
from typing import Any, Callable

from aio_pika import IncomingMessage, Message
from aio_pika.abc import AbstractRobustConnection, DeliveryMode


class RabbitMQConsumer:
    def __init__(
            self,
            rabbit_connection: AbstractRobustConnection,
            exchange_name: str,
            exchange_type: str,
            routing_key: str,
            callback: Callable,
            callback_data: Any,
            exchange_durable: bool = False,
            exchange_auto_delete: bool = True
    ):
        self.connection = rabbit_connection
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.exchange_auto_delete = exchange_auto_delete
        self.callback = callback
        self.callback_data = callback_data
        self.routing_key = routing_key
        self.channel = None
        self.exchange = None
        self.queue = None
        self.queue_name = None
        self.consumer_tag = None

    async def connect(self):
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            self.exchange_type,
            durable=self.exchange_durable,
            auto_delete=self.exchange_auto_delete
        )

        self.queue = await self.channel.declare_queue(
            name=self.queue_name,
            auto_delete=True,
            durable=False,
        )
        await self.queue.bind(self.exchange, routing_key=self.routing_key)
        self.consumer_tag = await self.queue.consume(self._on_consume_message)

    async def disconnect(self) -> None:
        """
        Disconnects from RabbitMQ
        """
        if not self.channel.is_closed:
            await self.queue.cancel(self.consumer_tag)
            await self.queue.unbind(self.exchange, routing_key=self.routing_key, timeout=1)
            if self.queue and self.queue_name is None:
                await self.queue.delete()
            await self.channel.close()

    async def _on_consume_message(self, incoming_message: IncomingMessage) -> None:
        try:
            if self.callback is not None:
                message_body = incoming_message.body.decode()

                message_dict = {
                    **incoming_message.info(),
                    'body': message_body
                }
                if self.callback_data:
                    await self.callback(message_dict, self.callback_data)
                else:
                    await self.callback(message_dict)

            await incoming_message.ack()
        except Exception as e:  # pylint: disable = broad-except
            print(e)
            await incoming_message.nack()
