"""
Provides callbacks for rabbitmq
"""
from datetime import datetime, timezone
import json

from billing import const
from billing.dao.dao_tasks import handle_task_data


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


async def _handle_assigned_task(task_id, dao_operations, dao_tasks):
    """
    Operations to handle:
     - reduce personal balance
     - increase company's income

    """
    task = await dao_tasks.get(task_id)
    billing_cycle = await dao_operations.get_current_billing_cycle()
    billing_cycle_id = billing_cycle[const.BILLING_CYCLE_ID]
    credit = 0
    debit = task[const.ASSIGN_PRICE]
    operation_time = datetime.now(timezone.utc).isoformat()
    operation = {
        const.BILLING_CYCLE_ID: billing_cycle_id,
        const.TIME: operation_time,
        const.TASK_ID: task_id,
        const.WORKER_ID: task[const.ASSIGNED_WORKER_ID],
        const.CREDIT: credit,
        const.DEBIT: debit
    }
    await dao_operations.add(operation)


async def _handle_finished_task(task_id, dao_operations, dao_tasks):
    """
    Increases balance of
    """
    task = await dao_tasks.get(task_id)
    billing_cycle = await dao_operations.get_current_billing_cycle()
    billing_cycle_id = billing_cycle[const.BILLING_CYCLE_ID]
    credit = task[const.FINISH_PRICE]
    debit = 0
    operation_time = datetime.now(timezone.utc).isoformat()
    operation = {
        const.BILLING_CYCLE_ID: billing_cycle_id,
        const.TIME: operation_time,
        const.TASK_ID: task_id,
        const.WORKER_ID: task[const.ASSIGNED_WORKER_ID],
        const.CREDIT: credit,
        const.DEBIT: debit
    }
    await dao_operations.add(operation)


async def task_workflow_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    data = message_body['data']
    event = message_body['event_name']

    if event == const.EVENT__TASK_ASSIGNED_1:
        task_id = data['assigned_task_id']
        await _handle_assigned_task(
            task_id,
            app['dao_operations'],
            app['dao_tasks']
        )  # списать бабки

    if event == const.EVENT__TASK_FINISHED_1:
        task_id = data['assigned_task_id']
        await _handle_finished_task(
            task_id,
            app['dao_operations'],
            app['dao_tasks']
        )  # начислить бабки
