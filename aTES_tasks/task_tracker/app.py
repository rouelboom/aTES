"""
Application factory module
"""
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config

import aio_pika
from aiohttp import web
import aiohttp_cors


from aTES_tasks.task_tracker.db import init_engine
from aTES_tasks.task_tracker.dao.dao_task import DAOTask

from aTES_tasks.task_tracker.api.tasks import TaskTrackerService
from aTES_tasks.task_tracker.rmq.publisher import RabbitMQPublisher


async def on_app_start(app):
    """
    Service initialization on application start
    """
    assert 'config' in app
    config = app['config']

    engine = await init_engine()
    app['engine'] = engine

    rabbitmq_config = config['rabbitmq']

    rabbitmq_url = 'amqp://{}:{}@{}/'.format(
        rabbitmq_config["login"],
        rabbitmq_config["password"],
        rabbitmq_config["host"]
    )
    rabbit_connection = await aio_pika.connect_robust(rabbitmq_url)
    app['rabbit_connection'] = rabbit_connection
    task_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['task_streaming']['name'],
        exchange_type=config['exchanges']['task_streaming']['type']
    )
    await task_publisher.connect()
    app['task_publisher'] = task_publisher

    app['dao'] = DAOTask(engine)


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    await app['common_exchange_publisher'].close()

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
