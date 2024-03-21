"""
Provides tools for publishing messages
"""
from datetime import datetime
import json
import uuid

from billing.exceptions import InvalidParams
from billing.rmq.publisher import RabbitMQPublisher


def get_default_message_data(version: int = 1) -> dict:
    return {
        'event_time': datetime.now(),
        'event_version': version,
        'event_id': uuid.uuid4().hex
    }


def get_message(self, obj: dict, event_name: str):
    message = {
        **get_default_message_data(version=1),
        'event_name': event_name,
        'data': obj,
    }
    errors = self.schema_validator.validate(message, event_name)
    if errors:
        print('>>>>> Event data is not valid:')
        print('>>>>> data: %s', message)
        raise InvalidParams
    return message


def publish_message(
        publisher: RabbitMQPublisher,
        routing_key: str,
        message: dict):
    await publisher.publish(routing_key, json.dumps(message))
