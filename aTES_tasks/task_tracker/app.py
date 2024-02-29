"""
Application factory module
"""
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config
import json

from aiohttp import web
import aiohttp_cors


# from aio_pika import Connection

# from aio_pika import Consumer


from aTES_tasks.task_tracker.api import const
from aTES_tasks.task_tracker.db import init_engine
from aTES_tasks.task_tracker.dao.dao_task import DAOTask

from aTES_tasks.task_tracker.api.task_tracker import TaskTrackerService

logger = logging.getLogger('app')


async def audit_object_info_queue_callback(message, data):
    """
    Callback function for audit object-info consumer,
    which deletes document by cascade when a person was deleted.
    """
    try:
        app = data  # type: web.Application
        obj_info = json.loads(message['body'])  # type: dict
        # TODO: add your code here. Don't forget to test it
    except Exception:  # pylint: disable = broad-except
        logger.exception('Error processing object info from RabbitMQ')


async def on_app_start(app):
    """
    Service initialization on application start
    """
    assert 'config' in app
    config = app['config']

    asyncio.get_event_loop().set_default_executor(ThreadPoolExecutor(max_workers=config['thread_pool_size']))

    logger.info('Init Database engine')

    engine = await init_engine()
    app['engine'] = engine
    #
    # rabbitmq_config = config['rabbitmq']
    # rabbitmq_connection = Connection(
    #     host=rabbitmq_config['host'],
    #     port=rabbitmq_config['port'],
    #     login=rabbitmq_config['login'],
    #     password=rabbitmq_config['password']
    # )
    # await rabbitmq_connection.connect()
    # app['rabbitmq_connection'] = rabbitmq_connection
    #
    # audit_object_info_exchange_props = config['exchanges']['audit_object_info']
    # audit_object_info_queue_props = config['audit_object_info_queue']
    # audit_object_info_consumer = Consumer(
    #     connection=rabbitmq_connection,
    #     exchange_name=audit_object_info_exchange_props['name'],
    #     exchange_type=audit_object_info_exchange_props['type'],
    #     exchange_durable=audit_object_info_exchange_props.get('durable', False),
    #     exchange_auto_delete=audit_object_info_exchange_props.get('auto_delete', True),
    #     queue_name=audit_object_info_queue_props['name'],
    #     routing_key='#',  # TODO: change routing key if it's needed
    #     queue_durable=audit_object_info_queue_props.get('durable', False),
    #     queue_auto_delete=audit_object_info_queue_props.get('auto_delete', True),
    #     callback=audit_object_info_queue_callback,
    #     callback_data=app
    # )
    # await audit_object_info_consumer.connect()
    # app['audit_object_info_consumer'] = audit_object_info_consumer

    app['dao'] = DAOTask(engine)


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    # await app['audit_object_info_consumer'].disconnect()
    # await app['rabbitmq_connection'].disconnect()
    
    
    app['engine'].close()
    await app['engine'].wait_closed()


# pylint: disable = unused-argument
def create_app(loop: AbstractEventLoop = None, config: dict = None) -> web.Application:
    """
    Creates a web application

    Args:
        loop:
            loop is needed for pytest tests with pytest-aiohttp plugin.
            It is intended to be passed to web.Application, but
            it's deprecated there. So, it remains to avoid errors in tests.
        config:
            dictionary with configuration parameters

    Returns:
        application

    """
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    cors.add(app.router.add_route('*', '/jsonrpc/tasks', TaskTrackerService))

    app['config'] = config
    logging.config.dictConfig(config['logging'])

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
