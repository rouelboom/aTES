"""
Provides callbacks for rabbitmq
"""
import json

from bills.api import const
from bills.dao.dao_tasks import handle_task_data


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
    data = message_body['data']
    event = message_body['event_name']

    if event in (const.EVENT__TASK_CREATED, const.EVENT__TASK_UPDATED):
        task = {
            'id': data['id'],
            'name': data['name'],
            'description': data['description'],
            'assigned_worker': data['description']
        }
        await handle_task_data(task, app['dao_tasks'])
        return


async def _handle_assigned_task(task, dao_operations, dao_company_income, dao_tasks):
    """
    Operations to handle:
     - reduce personal balance
     - increase company's income

    """
    task


async def task_workflow_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    data = message_body['data']
    event = message_body['event_name']

    if event == const.EVENT__TASK_ASSIGNED_1:
        task_id = data['assigned_task_id']
        task = {
            const.ID: data['assigned_task_id'],
            const.ASSIGNED_WORKER: data['finisher_id'],
        }
        await handle_task_data(
            task,
            app['dao_tasks']
        )
        await _handle_assigned_task(
            task_id,
            app['dao_operations'],
            app['dao_company_income'],
            app['dao_tasks']
        )  # списать бабки

    if event == const.EVENT__USER_UPDATED:
        await app['dao_tasks'].set({
            'id': data['id'],
            'name': data['name'],
            'description': data['description'],
            'assigned_worker': data['description']
        })
        return
