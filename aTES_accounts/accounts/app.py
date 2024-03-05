"""
Application factory module
"""
from asyncio import AbstractEventLoop

import aio_pika
from aiohttp import web
import aiohttp_cors

from accounts.db import init_engine
from accounts.dao.dao_users import DAOUsers

from accounts.api.users import UsersService
from accounts.rmq.publisher import RabbitMQPublisher


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
    user_publisher = RabbitMQPublisher(
        rabbit_connection,
        exchange_name=config['exchanges']['user_streaming']['name'],
        exchange_type=config['exchanges']['user_streaming']['type']
    )
    await user_publisher.connect()
    app['user_publisher'] = user_publisher

    app['dao_users'] = DAOUsers(engine)


async def on_app_stop(app):
    """
    Stop accounts on application destroy
    """
    await app['rabbit_connection'].close()
    await app['user_publisher'].disconnect()

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

    cors.add(app.router.add_route('*', '/jsonrpc/users', UsersService))
    cors.add(app.router.add_route('*', '/jsonrpc/auth', UsersService))  # todo need new endpoint view

    app['config'] = config

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
