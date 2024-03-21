"""
Provides callbacks for rabbitmq
"""
from datetime import datetime, timezone
import json

from analytics import const
from analytics.dao.dao_tasks import handle_task_data
from analytics.rmq.message_publishing import get_message, publish_message
from analytics.rmq.publisher import RabbitMQPublisher
from analytics.schema_registry.validator import SchemaRegistryValidator


async def user_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    data = message_body['data']
    event = message_body['event_name']

    if event == const.EVENT__USER_CREATED:
        await app['dao_users'].add({
            'id': data['id'],
            'login': data['name'],
            'role': data['description']
        })
        return
    if event == const.EVENT__USER_UPDATED:
        await app['dao_users'].set({
            'id': data['id'],
            'login': data['name'],
            'role': data['description']
        })
        return
    if event == const.EVENT__USER_DELETED:
        await app['dao_users'].delete(data['id'])
        return


async def task_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    task = message_body['data']
    event = message_body['event_name']

    if event in (const.EVENT__TASK_CREATED, const.EVENT__TASK_UPDATED):
        await handle_task_data(task, app['dao_tasks'])
        return


async def price_streaming_callback(message, data):
    print(message, data)


async def operation_streaming_callback(message, data):
    print(message, data)
