"""
Validation schemas
"""
from typing import Dict

from cerberus import Validator

from bills import const

ECHO = {
    'message': {
        'type': 'string'
    }
}


ADD = {
    const.ID: {
        'type': 'string',
        'coerce': 'strip'
    },
    const.TASK_NAME: {
        'type': 'string',
        'coerce': 'strip'
    },
    const.DESCRIPTION: {
        'type': 'string',
        'coerce': 'strip'
    }
}

SET = {
    const.ID: {
        'type': 'string',
        'coerce': 'strip',
        'required': True
    },
    const.TASK_NAME: {
        'type': 'string',
        'coerce': 'strip'
    },
    const.DESCRIPTION: {
        'type': 'string',
        'coerce': 'strip'
    }
}

GET = {
    const.ID: {
        'type': 'string'
    }
}

DELETE = {
    const.ID: {
        'type': 'string'
    }
}

STRING_FILTER = {
    'like': {
        'type': 'string',
        'coerce': 'strip',
        'minlength': 1,
        'excludes': ['ilike', 'value']
    },
    'ilike': {
        'type': 'string',
        'coerce': 'strip',
        'minlength': 1,
        'excludes': ['like', 'value']
    },
    'values': {
        'type': 'list',
        'minlength': 1,
        'excludes': ['like', 'ilike'],
        'schema': {
            'type': 'string'
        }
    }
}

SIMPLE_FILTER = {
    const.SIMPLE_FILTER_QUERY: {
        'type': 'string',
        'coerce': 'strip'
    }
}

FILTER = {
    const.ID: {
        'type': 'dict',
        'schema': {
            'values': {
                'type': 'list',
                'schema': {
                    'type': 'string'
                }
            }
        }
    },
    const.TASK_NAME: {
        'type': 'dict',
        'schema': STRING_FILTER
    },
    const.SIMPLE_FILTER: {
        'type': 'dict',
        'schema': SIMPLE_FILTER
    },



}

ORDER = {
    'field': {
        'type': 'string',
        'allowed': [const.TASK_NAME]
    },
    'direction': {
        'type': 'string',
        'allowed': ['asc', 'desc']
    }
}

GET_COUNT_BY_FILTER = {
    'filter': {
        'type': 'dict',
        'schema': FILTER
    }
}

GET_LIST_BY_FILTER = {
    'filter': {
        'type': 'dict',
        'schema': FILTER
    },
    'order': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': ORDER
        }
    },
    'limit': {
        'type': 'integer',
        'min': 1
    },
    'offset': {
        'type': 'integer',
        'min': 0
    }
}


def validate_task(obj: dict, schema: dict) -> Dict[str, list]:
    """
    Validate

    Returns:
        A dict with errors. Empty when no errors were detected
    """

    validator = Validator(schema)
    validator.validate(obj)

    return validator.errors

