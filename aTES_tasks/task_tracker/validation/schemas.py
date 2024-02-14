"""
Validation schemas
"""
from task_tracker.api import const



ECHO = {
    'message': {
        'type': 'string'
    }
}


ADD = {
    'task': {
        'type': 'dict',
        'schema': {
            const.TASK_ID: {
                'type': 'string',
                'coerce': 'strip'
            },
            const.TASK_NAME: {
                'type': 'string',
                'coerce': 'strip'
            }
        }
    }
}

SET = {
    'task': {
        'type': 'dict',
        'schema': {
            const.TASK_ID: {
                'type': 'string',
                'coerce': 'strip',
                'required': True
            },
            const.TASK_NAME: {
                'type': 'string',
                'coerce': 'strip'
            }
        }
    }
}

GET = {
    const.TASK_ID: {
        'type': 'string'
    }
}

DELETE = {
    const.TASK_ID: {
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
    const.TASK_ID: {
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


