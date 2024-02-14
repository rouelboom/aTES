"""
Application factory module
"""
import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config
import socket
import json

from aiohttp import web
import aiohttp_cors
from m7_aiohttp.auth.service_token import AioHttpServiceToken
from m7_aiohttp.util.docs import handle_jsonrpc_doc
from m7_aiohttp.auth.access import AccessAioHttp
from m7_aiohttp.auth.token_tool import AioHttpTokenTool



from m7_aio_rabbitmq.connection import Connection

from m7_aio_rabbitmq.consumer import Consumer


from m7_data_obfuscator import load_credentials_file

import task_tracker
from task_tracker.m7 import m7_const
from task_tracker.api import const
from task_tracker.db import init_engine
from task_tracker.dao.dao_task_tracker import DAOTask
# TODO import your DAO classes here

from task_tracker.api.task_tracker import TaskTrackerService
from task_tracker.localization import set_lang
# TODO import your service classes here

logger = logging.getLogger('app')


def get_local_addr():
    """
    Returns local address
    """
    return socket.gethostbyname(socket.gethostname())


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

    if 'lang' in config['m7']:
        set_lang(config['m7']['lang'])


    assert 'database' in app['config']

    logger.info('Init Database engine')
    database_config = config['m7']['postgresql'].copy()
    database_config.update(config['database'])
    engine = await init_engine(database_config)
    app['engine'] = engine



    rabbitmq_props = config['m7']['rabbitmq']
    rabbitmq_credentials = load_credentials_file(rabbitmq_props['credentials_file'])
    rabbitmq_connection = Connection(
        host=rabbitmq_props['host'],
        port=rabbitmq_props['port'],
        login=rabbitmq_credentials['login'],
        password=rabbitmq_credentials['password']
    )
    await rabbitmq_connection.connect()
    app['rabbitmq_connection'] = rabbitmq_connection


    audit_object_info_exchange_props = config['m7']['exchanges']['audit_object_info']



    audit_object_info_queue_props = config['audit_object_info_queue']
    audit_object_info_consumer = Consumer(
        connection=rabbitmq_connection,
        exchange_name=audit_object_info_exchange_props['name'],
        exchange_type=audit_object_info_exchange_props['type'],
        exchange_durable=audit_object_info_exchange_props.get('durable', False),
        exchange_auto_delete=audit_object_info_exchange_props.get('auto_delete', True),
        queue_name=audit_object_info_queue_props['name'],
        routing_key='#',  # TODO: change routing key if it's needed
        queue_durable=audit_object_info_queue_props.get('durable', False),
        queue_auto_delete=audit_object_info_queue_props.get('auto_delete', True),
        callback=audit_object_info_queue_callback,
        callback_data=app
    )
    await audit_object_info_consumer.connect()
    app['audit_object_info_consumer'] = audit_object_info_consumer




    app['dao'] = DAOTask(engine)

    # TODO create your DAO objects here



    token_tool = AioHttpTokenTool(config['m7']['endpoints']['public_key'])
    app['token_tool'] = token_tool
    app['access'] = AccessAioHttp(token_tool)

    user_agent = 'task-tracker/{}'.format(task_tracker.__version__)

    service_token = AioHttpServiceToken(
        config['m7']['endpoints']['auth_v2'],
        config['m7']['credentials_file'],
        user_agent=user_agent
    )
    app['service_token'] = service_token

    root_domain = config['m7']['root_domain']
    app_url = 'http://task-tracker.{}'.format(root_domain)
    app_icon_url = config['m7']['endpoints']['cdn'] + config['resources']['icon_url']
    
    

    await token_tool.start()
    await service_token.start()






    # TODO start your components here


async def on_app_stop(app):
    """
    Stop tasks on application destroy
    """
    # TODO stop your components here
    
    
    
    await app['audit_object_info_consumer'].disconnect()
    
    
    await app['rabbitmq_connection'].disconnect()
    
    
    await app['token_tool'].stop()
    await app['service_token'].stop()
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

    cors.add(app.router.add_route('*', '/jsonrpc/task-tracker', TaskTrackerService))

    cors.add(app.router.add_route('GET', '/jsonrpc/task-tracker/doc', handle_jsonrpc_doc(TaskTrackerService)))




    app['config'] = config
    logging.config.dictConfig(config['logging'])

    app.on_startup.append(on_app_start)
    app.on_shutdown.append(on_app_stop)

    return app
