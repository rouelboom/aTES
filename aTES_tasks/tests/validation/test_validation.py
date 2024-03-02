"""
Tests of validation schemas
"""
import pytest

from m7_cerberus.m7_validator import M7Validator
from m7_pytest_compare.anything import ANYTHING

from task_tracker.validation import schemas
from task_tracker.api import const

TEST_DATA_ECHO = [
    (
        {
            'message': 'Test message'
        },
        {}
    ),
    (
        {
            'message': 42
        },
        {
            'message': ANYTHING
        }
    )
]


@pytest.mark.parametrize('data, errors', TEST_DATA_ECHO)
def test_echo(data, errors):
    """
    Test data for method 'echo'
    """
    validator = M7Validator(schemas.ECHO)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_ADD = [
    (
        {
            'task': {
                const.ID: 'some-id',
                const.TASK_NAME: 'Name'
            }
        },
        {}
    ),
    (
        {
            'task': {
                const.TASK_NAME: 'Name'
            }
        },
        {}
    ),
    (
        {
            'task': {
                const.ID: 42,
                const.TASK_NAME: 'Name'
            }
        },
        {
            'task': [{
                const.ID: ANYTHING
            }]
        }
    ),
    (
        {
            'task': {
                const.ID: 'some-id',
                const.TASK_NAME: 42
            }
        },
        {
            'task': [{
                const.TASK_NAME: ANYTHING
            }]
        }
    ),

    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_ADD)
def test_add(data, errors):
    """
    Test data for method 'add'
    """
    validator = M7Validator(schemas.ADD)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_SET = [
    (
        {
            'task': {
                const.ID: 'some-id',
                const.TASK_NAME: 'Name'
            }
        },
        {}
    ),
    (
        {
            'task': {
                const.TASK_NAME: 'Name'
            }
        },
        {
            'task': [{
                const.ID: ANYTHING
            }]
        }
    ),
    (
        {
            'task': {
                const.ID: 42,
                const.TASK_NAME: 'Name'
            }
        },
        {
            'task': [{
                const.ID: ANYTHING
            }]
        }
    ),
    (
        {
            'task': {
                const.ID: 'some-id',
                const.TASK_NAME: 42
            }
        },
        {
            'task': [{
                const.TASK_NAME: ANYTHING
            }]
        }
    ),

    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_SET)
def test_set(data, errors):
    """
    Test data for method 'set'
    """
    validator = M7Validator(schemas.SET)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_GET = [
    (
        {
            'id': 'some-id'
        },
        {}
    ),
    (
        {
            'id': 42
        },
        {
            'id': ANYTHING
        }
    ),

    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_GET)
def test_get(data, errors):
    """
    Test data for method 'get'
    """
    validator = M7Validator(schemas.GET)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_DELETE = [
    (
        {
            'id': 'some-id'
        },
        {}
    ),
    (
        {
            'id': 42
        },
        {
            'id': ANYTHING
        }
    ),

    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_DELETE)
def test_delete(data, errors):
    """
    Test data for method 'delete'
    """
    validator = M7Validator(schemas.DELETE)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_GET_COUNT_BY_FILTER = [
    (
        {
            'filter': {
                const.ID: {
                    'values': ['id-1', 'id-2']
                }
            }
        },
        {}
    ),
    (
        {
            'filter': {
                const.TASK_NAME: {
                    'ilike': '%something%'
                }
            }
        },
        {}
    ),
    (
        {
            'filter': {
                const.SIMPLE_FILTER: {
                    const.SIMPLE_FILTER_QUERY: 'query'
                }
            }
        },
        {}
    ),
    (
        {
            'filter': {
                const.ID: {
                    'values': [41, 42]
                }
            }
        },
        {
            'filter': [{
                const.ID: ANYTHING
            }]
        }
    ),
    (
        {
            'filter': {
                const.TASK_NAME: {
                    'ilike': 42
                }
            }
        },
        {
            'filter': [{
                const.TASK_NAME: ANYTHING
            }]
        }
    ),
    (
        {
            'filter': {
                const.SIMPLE_FILTER: {
                    const.SIMPLE_FILTER_QUERY: 42
                }
            }
        },
        {
            'filter': [{
                const.SIMPLE_FILTER: ANYTHING
            }]
        }
    ),

    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_GET_COUNT_BY_FILTER)
def test_get_count_by_filter(data, errors):
    """
    Test data for method 'get_count_by_filter'
    """
    validator = M7Validator(schemas.GET_COUNT_BY_FILTER)
    validator.validate(data)
    assert validator.errors == errors


TEST_DATA_GET_LIST_BY_FILTER = [
    (
        {
            'filter': {},
            'order': [],
            'limit': 10,
            'offset': 0
        },
        {}
    ),
    (
        {
            'filter': {
                const.ID: {
                    'values': ['id-1', 'id-2']
                }
            },
            'order': [{
                'field': const.TASK_NAME,
                'direction': 'desc'
            }],
            'limit': 10,
            'offset': 0
        },
        {}
    ),
    (
        {
            'filter': {},
            'order': [{
                'field': 'unknown-field',
                'direction': 'desc'
            }],
            'limit': 10,
            'offset': 0
        },
        {
            'order': ANYTHING
        }
    ),
    (
        {
            'filter': {},
            'order': [],
            'limit': 0,
            'offset': -1
        },
        {
            'limit': ANYTHING,
            'offset': ANYTHING
        }
    ),


    # TODO add your test cases here
]


@pytest.mark.parametrize('data, errors', TEST_DATA_GET_LIST_BY_FILTER)
def test_get_list_by_filter(data, errors):
    """
    Test data for method 'get_list_by_filter'
    """
    validator = M7Validator(schemas.GET_LIST_BY_FILTER)
    validator.validate(data)
    assert validator.errors == errors



