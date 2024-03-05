"""
Common tools
"""
from datetime import datetime
import uuid


def get_default_message_data(version: int = 1) -> dict:
    return {
        'event_time': datetime.now(),
        'event_version': version,
        'event_id': uuid.uuid4().hex
    }
