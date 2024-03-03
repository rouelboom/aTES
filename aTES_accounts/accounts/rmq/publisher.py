"""
Provides tool publishing messages to rabbitmq
"""
import asyncio

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractRobustConnection, DeliveryMode


class RabbitMQPublisher:
    def __init__(
            self,
            rabbit_connection: AbstractRobustConnection,
            exchange_name: str,
            exchange_type: str,
            exchange_durable: bool = False,
            exchange_auto_delete: bool = True
    ):
        self.connection = rabbit_connection
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.exchange_auto_delete = exchange_auto_delete

        self.channel = None
        self.exchange = None

    async def connect(self):
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            self.exchange_type,
            durable=self.exchange_durable,
            auto_delete=self.exchange_auto_delete
        )

    async def disconnect(self) -> None:
        """
        Disconnects from RabbitMQ
        """
        if self.channel and not self.channel.is_closed:
            await self.channel.close()

    async def publish(
            self,
            routing_key: str,
            message_body: str,
            correlation_id: str = None,
            persistent: bool = False
    ) -> None:
        """
        Publish message to RabbitMQ

        Args:
            routing_key: routing key
            message_body: message
            correlation_id:
            persistent: flag message to keep it on hard disk by RabbitMQ

        """
        print('Publisher %s: enqueue %s', self.exchange_name, message_body)
        message = Message(
            message_body.encode(),
            correlation_id=correlation_id,
            delivery_mode=DeliveryMode.PERSISTENT if persistent else DeliveryMode.NOT_PERSISTENT
        )
        print('routing_key = ', routing_key)
        await self.exchange.publish(
            message,
            routing_key=routing_key,
        )
        print('Message %s sent', message)
