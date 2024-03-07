"""
Provides callbacks for rabbitmq
"""
from datetime import datetime, timezone
import json

from bills import const
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


async def _handle_assigned_task(task_id, dao_operations, dao_company_income, dao_tasks):
    """
    Operations to handle:
     - reduce personal balance
     - increase company's income

    """
    task = await dao_tasks.get(task_id)
    assigned_price = task[const.ASSIGN_PRICE] * -1
    operation_time = datetime.now(timezone.utc).isoformat()
    operation = {
        const.PRICE: assigned_price,
        const.TIME: operation_time,
        const.SOURCE_ID: task_id,
        const.WORKER_ID: task[const.ASSIGNED_WORKER]
    }
    await dao_operations.add(operation)  # TODO внутри dao_operations.add надо в рамках одной транзакции уменьшать баланс пользователя и увеличивать баланс компании




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
