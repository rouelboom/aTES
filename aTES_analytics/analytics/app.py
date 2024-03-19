"""
Application factory module
"""
from asyncio import AbstractEventLoop

import aio_pika
from aiohttp import web
import aiohttp_cors

from analytics.dao.dao_billing import DAOBilling
from analytics.dao.dao_users import DAOUsers
from analytics.db import init_engine
from analytics.dao.dao_tasks import DAOTasks

from analytics.api.analytics import AnalyticsService
from analytics.rmq.callbacks import user_callback
from analytics.rmq.consumer import RabbitMQConsumer
from analytics.rmq.publisher import RabbitMQPublisher
from analytics.schema_registry.validator import SchemaRegistryValidator


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
    operation_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['operation_streaming']['name'],
        exchange_type=config['exchanges']['operation_streaming']['type']
    )
    await operation_publisher.connect()
    app['operation_publisher'] = operation_publisher

    analytics_event_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['analytics']['name'],
        exchange_type=config['exchanges']['analytics']['type']
    )
    await analytics_event_publisher.connect()
    app['analytics_event_publisher'] = analytics_event_publisher

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

    task_consumer = RabbitMQConsumer(
        rabbit_connection,
        exchange_name=config['exchange_subscriptions']['task_streaming'],
        exchange_type='topic',
        routing_key='*.task',
        callback=user_callback,
        callback_data=app
    )
    await task_consumer.connect()
    app['task_consumer'] = task_consumer

    app['dao_tasks'] = DAOTasks(engine)
    app['dao_users'] = DAOUsers(engine)
    app['dao_analytics'] = DAOBilling(engine)

    app['schema_validator'] = SchemaRegistryValidator(config['schemas_dir_path'])


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    await app['rabbit_connection'].close()
    await app['operation_publisher'].disconnect()
    await app['analytics_event_publisher'].disconnect()
    await app['user_consumer'].disconnect()
    await app['task_consumer'].disconnect()

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

    cors.add(app.router.add_route('*', '/jsonrpc/analytics', AnalyticsService))

    app['config'] = config

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
