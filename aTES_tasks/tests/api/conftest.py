"""
Pytest plugins
"""
import uuid
import asyncio
from pathlib import Path

import pytest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp_jsonrpc_algont.client import ServerProxy

from m7_aiohttp.auth.access import Unauthorized, Forbidden
from m7_aiohttp.exceptions import NotFound, InvalidParams
from pym7auth import M7_AUTH_TOKEN_HEADER

from alembic.command import upgrade

from tests.api.conf import TEST_CONFIG_PROFILE
from m7_pytest_postgres.alembic_utils import alembic_config_from_url
from m7_pytest_postgres.postgres import PostgresDatabaseProps





from task_tracker.api.exceptions import CustomException
from task_tracker.app import create_app
from task_tracker.db import Task, init_engine


class CustomServerProxy(ServerProxy):
    """
    Custom server proxy for definition of exceptions codes mapping
    """
    __JSONRPC_CODES__ = {
        Unauthorized.code: Unauthorized,
        Forbidden.code: Forbidden,
        InvalidParams.code: InvalidParams,
        NotFound.code: NotFound,
        CustomException.code: CustomException
    }


@pytest.fixture(scope='module')
def initialized_database(request, postgres_database) -> PostgresDatabaseProps:
    """
    Pytest fixture for creating temporary Postgres database
    """
    print('Initialize database - {}'.format(postgres_database.url))

    print('Upgrade database schema public to head revision')
    alembic_config = alembic_config_from_url(postgres_database.url, 'public', request.config.rootdir)
    upgrade(alembic_config, 'head')
    print('Database is ready')

    yield postgres_database


async def clear_database(config: dict):
    """
    Remove all data from database
    """
    database_config = config['m7']['postgresql'].copy()
    database_config.update(config['database'])
    engine = await init_engine(database_config)
    async with engine.acquire() as conn:
        async with conn.begin():
            await conn.execute(Task.delete())
            # TODO add more commands to clean database


# pylint: disable = too-few-public-methods
class FixtureServices:
    """
    Service endpoints and other objects for tests
    """
    def __init__(self, http_client, task_tracker, m7_accounts_auth_v2,
                 
                 
                 
                 ):
        """
        TODO add your endpoints as parameters of constructor
        """
        self.http_client = http_client
        self.task_tracker = task_tracker
        # TODO store your endpoints from parameters here
        self.m7_accounts_auth_v2 = m7_accounts_auth_v2
        
        
        
        
        
        
        
        
        

    def inject_token(self, token: str):
        """
        Inject authentication token to all service clients except 'auth'
        """
        self.task_tracker.headers[M7_AUTH_TOKEN_HEADER] = token
        
        
        
        
        # TODO inject token to your endpoints here

    async def close(self):
        """
        Closes all clients
        """
        # TODO close your endpoints here
        await self.task_tracker.close()
        
        
        
        
        
        
        
        await self.m7_accounts_auth_v2.close()


# pylint: disable = too-many-arguments
@pytest.fixture
def service_clients(event_loop, initialized_database, m7_accounts_mock,
                    
                    rabbitmq_connection_props, rabbitmq_connection,
                    
                    ) -> FixtureServices:
    """
    Pytest fixture for creating named tuple with all endpoints of the accounts service
    """
    test_client = None
    rpc_clients = None

    asyncio.set_event_loop(event_loop)

    credentials_file_path = str(Path(__file__).parent.joinpath('service-credentials.json'))

    config = TEST_CONFIG_PROFILE.copy()
    config['database']['name'] = initialized_database.name
    config['m7']['endpoints']['public_key'] = m7_accounts_mock.public_key
    config['m7']['endpoints']['auth_v2'] = m7_accounts_mock.auth_v2
    
    
    
    config['m7']['credentials_file'] = credentials_file_path
    config['m7']['postgresql'] = initialized_database._asdict()
    config['m7']['rabbitmq'] = rabbitmq_connection_props._asdict()
    
    
    config['audit_object_info_queue']['name'] = "test.{}".format(uuid.uuid4().hex)


    @asyncio.coroutine
    def _create_from_app_factory(app_factory, *args, **kwargs):
        nonlocal test_client, rpc_clients
        app = app_factory(event_loop, *args, **kwargs)
        test_client = TestClient(TestServer(app), loop=event_loop)
        yield from test_client.start_server()

        rpc_clients = FixtureServices(
            http_client=test_client,
            task_tracker=CustomServerProxy('/jsonrpc/task-tracker', loop=event_loop, client=test_client),
            # TODO add your endpoints here
            m7_accounts_auth_v2=ServerProxy(m7_accounts_mock.auth_v2, loop=event_loop),
            
            
            
            
            
            
            
            
            
        )

        return rpc_clients

    event_loop.run_until_complete(clear_database(config))


    yield event_loop.run_until_complete(_create_from_app_factory(create_app, config=config))

    if rpc_clients:
        event_loop.run_until_complete(rpc_clients.close())
        rpc_clients = None

    if test_client:
        event_loop.run_until_complete(test_client.close())
        test_client = None
