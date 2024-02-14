"""
Tests of sample service
"""
import pytest
from pym7auth import ROLE_ADMIN

pytestmark = pytest.mark.asyncio


async def test_sample(service_clients):
    """
    Sample test for sample service
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # Do some actions
    echo = await service_clients.task_tracker.echo('Hello')
    assert echo == 'Hello'
