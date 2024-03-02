"""
Tests corresponding with database
"""
import pytest

from pym7auth import ROLE_ADMIN

from m7_aiohttp.exceptions import NotFound

from task_tracker.api import const

pytestmark = pytest.mark.asyncio

SAMPLE = {
    const.TASK_NAME: 'Sample name'
}


async def test_add(service_clients):
    """
    Test add
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ACT
    id = await service_clients.task_tracker.add(SAMPLE)
    assert id is not None

    # ASSERT
    test_sample = await service_clients.task_tracker.get(id)
    assert test_sample == {
        const.ID: id,
        **SAMPLE
    }


async def test_add_with_predefined_id(service_clients):
    """
    Test add with predefined object id
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ACT
    id = await service_clients.task_tracker.add({
        **SAMPLE,
        const.ID: 'id-42'
    })
    assert id == 'id-42'

    # ASSERT
    test_sample = await service_clients.task_tracker.get(id)
    assert test_sample == {
        const.ID: id,
        **SAMPLE
    }


async def test_set(service_clients):
    """
    Test change
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    await service_clients.task_tracker.set({
        const.ID: id,
        const.TASK_NAME: 'Changed name'
    })

    # ASSERT
    test_sample = await service_clients.task_tracker.get(id)
    assert test_sample == {
        const.ID: id,
        const.TASK_NAME: 'Changed name'
    }


async def test_delete(service_clients):
    """
    Test delete
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    await service_clients.task_tracker.delete(id)

    # ASSERT
    with pytest.raises(NotFound):
        await service_clients.task_tracker.get(id)


async def test_get_unknown(service_clients):
    """
    Test if exception is raised when try to get unknown object
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ASSERT
    with pytest.raises(NotFound):
        await service_clients.task_tracker.get('unknown id')


async def test_get_list_by_filter__by_name(service_clients):
    """
    Test get list by filter by name
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    list_1 = await service_clients.task_tracker.get_list_by_filter(
        {
            const.TASK_NAME: {
                'ilike': '%ampl%'
            }
        },
        [], 100, 0
    )

    list_2 = await service_clients.task_tracker.get_list_by_filter(
         {
             const.TASK_NAME: {
                 'ilike': '%unknown%'
             }
         },
         [], 100, 0
    )

    # ASSERT
    assert list_1 == [{
        **SAMPLE,
        const.ID: id,
    }]
    assert list_2 == []


async def test_get_list_by_filter__by_id(service_clients):
    """
    Test get list by filter by object id
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    list_1 = await service_clients.task_tracker.get_list_by_filter(
         {
             const.ID: {
                 'values': [id]
             }
         },
         [], 100, 0
    )

    list_2 = await service_clients.task_tracker.get_list_by_filter(
         {
             const.ID: {
                 'values': ['unknown-id']
             }
         },
         [], 100, 0
    )

    # ASSERT
    assert list_1 == [{
        **SAMPLE,
        const.ID: id,
    }]
    assert list_2 == []


async def test_get_list_by_filter__simple(service_clients):
    """
    Test get list by filter by name
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    list_1 = await service_clients.task_tracker.get_list_by_filter(
        {
            const.SIMPLE_FILTER: {
                const.SIMPLE_FILTER_QUERY: 'samp'
            }
        },
        [], 100, 0
    )

    list_2 = await service_clients.task_tracker.get_list_by_filter(
         {
            const.SIMPLE_FILTER: {
                const.SIMPLE_FILTER_QUERY: 'unknown'
            }
         },
         [], 100, 0
    )

    # ASSERT
    assert list_1 == [{
        **SAMPLE,
        const.ID: id,
    }]
    assert list_2 == []


async def test_get_list_by_filter_sorted(service_clients):
    """
    Test get lists with different order
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id_1 = await service_clients.task_tracker.add({
        **SAMPLE,
        const.TASK_NAME: 'Name 1'
    })
    item_1 = await service_clients.task_tracker.get(id_1)

    id_2 = await service_clients.task_tracker.add({
        **SAMPLE,
        const.TASK_NAME: 'Name 2'
    })
    item_2 = await service_clients.task_tracker.get(id_2)

    # ACT
    list_1 = await service_clients.task_tracker.get_list_by_filter(
        {},
        [{
            'field': const.TASK_NAME,
            'direction': 'asc'
        }],
        100, 0
    )

    list_2 = await service_clients.task_tracker.get_list_by_filter(
        {},
        [{
            'field': const.TASK_NAME,
            'direction': 'desc'
        }],
        100, 0
    )

    # ASSERT
    assert list_1 == [item_1, item_2]
    assert list_2 == [item_2, item_1]


async def test_get_count_by_filter__by_name(service_clients):
    """
    Test get count by filter by name
    """
    tokens = await service_clients.m7_accounts_auth_v2.login('test', '****', {'roles': [ROLE_ADMIN]})
    service_clients.inject_token(tokens['access_token'])

    # ARRANGE
    id = await service_clients.task_tracker.add(SAMPLE)

    # ACT
    count_1 = await service_clients.task_tracker.get_count_by_filter(
        {
            const.TASK_NAME: {
                'ilike': '%ampl%'
            }
        }
    )

    count_2 = await service_clients.task_tracker.get_count_by_filter(
         {
             const.TASK_NAME: {
                 'ilike': '%unknown%'
             }
         }
    )

    # ASSERT
    assert count_1 == 1
    assert count_2 == 0
