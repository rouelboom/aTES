"""
Constants of JSON-RPC service parameters
"""

ID = 'id'
TASK_NAME = 'name'

START_DATE = 'start_date'
END_DATE = 'end_date'

COMPANY_BALANCE_ID_VALUE = 'bd7d56207d5a42a2812b062e85706108'

# BUSINESS EVENTS
# вероятно я так и не понял, как правильно называть бизнес ивенты
# в данном случае у нас имя exchange - workflow
EVENT__TASK_ASSIGNED_1 = 'task.assigned.1'
EVENT__TASK_FINISHED_1 = 'task.finished.1'

# STREAMING EVENTS
EVENT__TASK_CREATED = 'created'
EVENT__TASK_UPDATED = 'updated'

EVENT__USER_CREATED = 'created'
EVENT__USER_UPDATED = 'updated'
EVENT__USER_DELETED = 'deleted'


NAME = 'name'
DESCRIPTION = 'description'
STATUS = 'status'
ASSIGNED_WORKER_ID = 'assigned_worker_id'

WORKER_ID = 'worker_id'
TIME = 'time'
MONEY_AMOUNT = 'money_amount'
FINISH_PRICE = 'finish_price'
ASSIGN_PRICE = 'assign_price'
TASK_ID = 'task_id'

OPENED = 'opened'
CLOSED = 'closed'
TASK_STATUS__FINISHED = 'finished'
TASK_STATUS__OPENED = OPENED
TASK_STATUS__IN_PROGRESS = 'in_progress'
STATUS__BILLING_CYCLE__OPENED = OPENED
STATUS__BILLING_CYCLE__CLOSED = CLOSED

LOGIN = 'login'
ROLE = 'role'

USER_ROLE__ADMIN = 'popug_admin'
USER_ROLE__WORKER = 'popug_worker'
USER_ROLE__MANAGER = 'popug_manager'

EVENT_VERSION_1 = 1

CREDIT = 'credit'
DEBIT = 'debit'

BILLING_CYCLE_ID = 'billing_cycle_id'
USER_ID = 'user_id'
VALUE = 'value'
