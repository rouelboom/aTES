"""
Application configuration template for tests
"""

TEST_CONFIG_PROFILE = {
    "m7": {
        "root_domain": "local",
        "lang": "en",
        "postgresql": {
            "host": "127.0.0.1"
        },
        "rabbitmq": {
            "host": "127.0.0.1",
            "port": 5672
        },
        "exchanges": {
        },
        "endpoints": {
            "cdn": "http://cdn.local"
        },
        "internal_endpoints": {

        }
    },
    'database': {
        'name': 'task',
    },
    "thread_pool_size": 5,
    "resources": {
        "icon_url": "/aTES/shared/task-tracker/img/logos/logo.svg"
    },
    
    "audit_object_info_queue": {
        "name": "aTES.task-tracker.object-info.queue"
    },
    
    'logging': {
        "version": 1,
        "handlers": {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'DEBUG'
            },
        },
        "loggers": {
            "app": {
                "level": "DEBUG",
            },
            "auth": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
        "formatters": {
            "default": {
                "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}
