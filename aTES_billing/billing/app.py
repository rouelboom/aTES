"""
Application factory module
"""
from asyncio import AbstractEventLoop

import aio_pika
from aiohttp import web
import aiohttp_cors

from billing.cron.daily import handle_daily_withdraw
from billing.dao.dao_billing import DAOBilling
from billing.dao.dao_users import DAOUsers
from billing.db import init_engine
from billing.dao.dao_tasks import DAOTasks

from billing.api.operations import OperationsService
from billing.rmq.callbacks import user_callback
from billing.rmq.consumer import RabbitMQConsumer
from billing.rmq.publisher import RabbitMQPublisher
from billing.schema_registry.validator import SchemaRegistryValidator


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

    billing_event_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['billing']['name'],
        exchange_type=config['exchanges']['billing']['type']
    )
    await billing_event_publisher.connect()
    app['billing_event_publisher'] = billing_event_publisher

    price_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['price_streaming']['name'],
        exchange_type=config['exchanges']['price_streaming']['type']
    )
    await price_publisher.connect()
    app['price_publisher'] = price_publisher

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
    app['dao_billing'] = DAOBilling(engine)

    app['schema_validator'] = SchemaRegistryValidator(config['schemas_dir_path'])


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    await app['rabbit_connection'].close()
    await app['operation_publisher'].disconnect()
    await app['billing_event_publisher'].disconnect()
    await app['user_consumer'].disconnect()
    await app['task_consumer'].disconnect()
    await app['price_publisher'].disconnect()

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

    app.router.add_route('GET', '/cron/daily-withdraw', handle_daily_withdraw)
    cors.add(app.router.add_route('*', '/jsonrpc/operations', OperationsService))

    app['config'] = config

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
