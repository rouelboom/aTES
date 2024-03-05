"""
Constants of JSON-RPC service parameters
"""

ID = 'id'

EVENT__USER_CREATED = 'created'
EVENT__USER_UPDATED = 'updated'
EVENT__USER_DELETED = 'deleted'

LOGIN = 'login'
BEAK_SHAPE = 'beak_shape'
ROLE = 'role'

USER_ROLE__ADMIN = 'popug_admin'
USER_ROLE__WORKER = 'popug_worker'
USER_ROLE__MANAGER = 'popug_worker'

ALLOWED_ROLES = [
    USER_ROLE__ADMIN,
    USER_ROLE__WORKER,
    USER_ROLE__MANAGER
]
