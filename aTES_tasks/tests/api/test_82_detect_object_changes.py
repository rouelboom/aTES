"""
Tests for object changes detection
"""
import pytest

pytestmark = pytest.mark.asyncio


async def test_detect_object_changes(service_clients, audit_object_info_publisher):
    """
    Tests object changes detection
    """
    # TODO: add your test code here