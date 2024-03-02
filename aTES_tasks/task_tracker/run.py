"""
Service running module
"""
import json

from aiohttp import web

from task_tracker.app import create_app


if __name__ == '__main__':
    config_file = '/Users/pavel/Dev/pets/aTES/aTES_tasks/config.json'
    with open(config_file) as f:
        config = json.load(f)
    app = create_app(config=config)
    web.run_app(
        app,
        host=config.get('host'),
        port=config.get('port'),
    )
