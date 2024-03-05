"""
Provides callbacks for rabbitmq
"""
import json

from task_tracker.api import const


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
