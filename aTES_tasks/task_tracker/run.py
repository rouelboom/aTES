"""
Service running module
"""
import json

import sys
import argparse
from aiohttp import web

from task_tracker.app import create_app


def get_config_files() -> tuple:
    """
    Gets configuration profile name

    Returns:
        tuple (service_config, m7_config)

    """
    parser = argparse.ArgumentParser(description='task-tracker service')
    parser.add_argument(
        '--config',
        help='configuration file name',
        type=str,
        default='/etc/aTES/services/task-tracker.json')
    parser.add_argument(
        '--m7config',
        help='M7 configuration file name',
        type=str,
        default='/etc/m7/m7.json')

    args, _ = parser.parse_known_args()
    if not args.config or not args.m7config:
        parser.print_usage()
        sys.exit(1)
    return args.config, args.m7config


if __name__ == '__main__':
    config_file, m7_config_file = get_config_files()
    with open(config_file) as f:
        config = json.load(f)
    with open(m7_config_file) as f:
        m7_config = json.load(f)
    config.update(m7_config)
    app = create_app(config=config)
    web.run_app(
        app,
        host=config.get('host'),
        port=config.get('port'),
        access_log_format=config.get('access_log_format')
    )
