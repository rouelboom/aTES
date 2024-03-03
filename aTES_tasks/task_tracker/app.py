"""
Application factory module
"""
from asyncio import AbstractEventLoop

import aio_pika
from aiohttp import web
import aiohttp_cors

from task_tracker.dao.dao_users import DAOUsers
from task_tracker.db import init_engine
from task_tracker.dao.dao_tasks import DAOTasks

from task_tracker.api.tasks import TaskTrackerService
from task_tracker.rmq.callbacks import user_callback
from task_tracker.rmq.consumer import RabbitMQConsumer
from task_tracker.rmq.publisher import RabbitMQPublisher


async def on_app_start(app):
    """
    Service initialization on application start
    """
    assert 'config' in app
    config = app['config']

    engine = await init_engine(config['database'])
    app['engine'] = engine

    rabbitmq_config = config['rabbitmq']
    rabbit_connection = await aio_pika.connect_robust(
        host=rabbitmq_config["host"],
        port=rabbitmq_config["port"],
        login=rabbitmq_config["login"],
        password=rabbitmq_config["password"]
    )

    app['rabbit_connection'] = rabbit_connection
    task_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['task_streaming']['name'],
        exchange_type=config['exchanges']['task_streaming']['type']
    )
    await task_publisher.connect()
    app['task_streaming_publisher'] = task_publisher

    business_event_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['task_business_events']['name'],
        exchange_type=config['exchanges']['task_business_events']['type']
    )
    await business_event_publisher.connect()
    app['business_event_publisher'] = business_event_publisher

    user_consumer = RabbitMQConsumer(
        rabbit_connection,
        exchange_name=config['exchange_subscriptions']['user_streaming'],
        exchange_type='topic',
        routing_key='*.user',
        callback=user_callback,
        callback_data=app
    )
    await user_consumer.connect()
    app['user_consumer'] = user_consumer

    app['dao_tasks'] = DAOTasks(engine)
    app['dao_users'] = DAOUsers(engine)


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    await app['rabbit_connection'].close()
    await app['task_streaming_publisher'].disconnect()
    await app['user_consumer'].disconnect()
    await app['business_event_publisher'].disconnect()

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

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
