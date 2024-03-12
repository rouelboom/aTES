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


async def _handle_assigned_task(task_id, dao_analytics, dao_tasks) -> dict:
    task = await dao_tasks.get(task_id)
    analytics_cycle = await dao_analytics.get_current_analytics_cycle()
    analytics_cycle_id = analytics_cycle[const.BILLING_CYCLE_ID]
    credit = 0
    debit = task[const.ASSIGN_PRICE]
    operation_time = datetime.now(timezone.utc).isoformat()
    operation = {
        const.BILLING_CYCLE_ID: analytics_cycle_id,
        const.TIME: operation_time,
        const.DESCRIPTION: task_id,
        const.WORKER_ID: task[const.ASSIGNED_WORKER_ID],
        const.CREDIT: credit,
        const.DEBIT: debit
    }
    operation[const.ID] = await dao_analytics.add_operation(operation)
    return operation


async def stream_new_operation(
        operation: dict,
        routing_key: str,
        publisher: RabbitMQPublisher,
        validator: SchemaRegistryValidator
):
    data = {
        **operation,
        const.OPERATION_ID: operation[const.ID]
    }
    data.pop(const.ID)
    message = get_message(data, const.EVENT__OPERATION_CREATED, validator)
    await publish_message(
        publisher,
        routing_key,
        message
    )


async def _handle_finished_task(task_id, dao_analytics, dao_tasks) -> dict:
    task = await dao_tasks.get(task_id)
    analytics_cycle = await dao_analytics.get_current_analytics_cycle()
    analytics_cycle_id = analytics_cycle[const.BILLING_CYCLE_ID]
    credit = task[const.FINISH_PRICE]
    debit = 0
    operation_time = datetime.now(timezone.utc).isoformat()
    operation = {
        const.BILLING_CYCLE_ID: analytics_cycle_id,
        const.TIME: operation_time,
        const.DESCRIPTION: task_id,
        const.WORKER_ID: task[const.ASSIGNED_WORKER_ID],
        const.CREDIT: credit,
        const.DEBIT: debit
    }
    operation[const.ID] = await dao_analytics.add_operation(operation)
    return operation


async def task_workflow_callback(message, data):
    message_body = json.loads(message['body'])
    app = data
    data = message_body['data']
    event = message_body['event_name']

    if event == const.EVENT__TASK_ASSIGNED_1:
        task_id = data['assigned_task_id']
        operation = await _handle_assigned_task(
            task_id,
            app['dao_analytics'],
            app['dao_tasks']
        )  # создать запись о том что бабки списаны

    if event == const.EVENT__TASK_FINISHED_1:
        task_id = data['assigned_task_id']
        operation = await _handle_finished_task(
            task_id,
            app['dao_analytics'],
            app['dao_tasks']
        )  # начислить бабки

    if event in (const.EVENT__TASK_FINISHED_1, const.EVENT__TASK_ASSIGNED_1):
        await stream_new_operation(
            operation,
            app['config']['exchanges']['operation_streaming']['name'],
            app['operation_publisher'],
            app['schema_validator']
        )
