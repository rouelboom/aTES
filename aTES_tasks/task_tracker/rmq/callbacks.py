"""
Provides callbacks for rabbitmq
"""
import json

from task_tracker.api import const


async def user_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    obj = message_body['object']
    event = message_body['event']

    if event == const.EVENT__USER_CREATED:
        await app['dao_users'].add({
            'id': obj['id'],
            'login': obj['name'],
            'role': obj['description']
        })
        return
    if event == const.EVENT__USER_UPDATED:
        await app['dao_users'].set({
            'id': obj['id'],
            'login': obj['name'],
            'role': obj['description']
        })
        return
    if event == const.EVENT__USER_DELETED:
        await app['dao_users'].delete(obj['id'])
        return
