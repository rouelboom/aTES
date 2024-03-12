"""
Provides tools for publishing messages
"""
from datetime import datetime
import json
import uuid

from analytics.exceptions import InvalidParams
from analytics.rmq.publisher import RabbitMQPublisher
from analytics.schema_registry.validator import SchemaRegistryValidator


def get_default_message_data(version: int = 1) -> dict:
    return {
        'event_time': datetime.now(),
        'event_version': version,
        'event_id': uuid.uuid4().hex
    }


def get_message(obj: dict, event_name: str, validator: SchemaRegistryValidator):
    errors = validator.validate(obj, event_name)
    if errors:
        print('>>>>> Event data is not valid:')
        print('>>>>> data: %s', obj)
        raise InvalidParams
    return {
        **get_default_message_data(version=1),
        'event_name': event_name,
        'data': obj,
    }


async def publish_message(
        publisher: RabbitMQPublisher,
        routing_key: str,
        message: dict):
    await publisher.publish(routing_key, json.dumps(message))
