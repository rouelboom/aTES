"""
Constants of JSON-RPC service parameters
"""

ID = 'id'
TASK_NAME = 'name'

# BUSINESS EVENTS
# вероятно я так и не понял, как правильно называть бизнес ивенты
# в данном случае у нас имя exchange - workflow
EVENT__TASK_ASSIGNED = 'task.assigned'
EVENT__TASK_FINISHED = 'task.finished'

# STREAMING EVENTS
EVENT__TASK_CREATED = 'created'
EVENT__TASK_UPDATED = 'updated'

EVENT__USER_CREATED = 'created'
EVENT__USER_UPDATED = 'updated'
EVENT__USER_DELETED = 'deleted'


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
USER_ROLE__MANAGER = 'popug_manager'

EVENT_VERSION_1 = 1
