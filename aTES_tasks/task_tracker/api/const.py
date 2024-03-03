"""
Constants of JSON-RPC service parameters
"""

ID = 'id'
TASK_NAME = 'name'

SIMPLE_FILTER = 'simple'
SIMPLE_FILTER_QUERY = 'query'

EVENT__TASK_CREATED = 'task.created'
EVENT__TASK_UPDATED = 'task.updated'
EVENT__TASK_DELETED = 'task.deleted'

EVENT__USER_CREATED = 'user.created'
EVENT__USER_UPDATED = 'user.updated'
EVENT__USER_DELETED = 'user.deleted'


NAME = 'name'
DESCRIPTION = 'description'
STATUS = 'status'
ASSIGNED_WORKER = 'assigned_worker'

TASK_STATUS__FINISHED = 'finished'
TASK_STATUS__OPENED = 'opened'
TASK_STATUS__IN_PROGRESS = 'in_progress'

LOGIN = 'login'
ROLE = 'role'

USER_ROLE__ADMIN = 'popug_admin'
USER_ROLE__WORKER = 'popug_worker'
