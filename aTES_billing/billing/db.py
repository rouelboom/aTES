"""
Database objects definitions
"""
from aiopg.sa import create_engine
from sqlalchemy import DateTime, Integer, MetaData, Table, Column, String, PrimaryKeyConstraint


async def init_engine(db_config) -> 'Engine':
    """
    Engine initialization
    """
    return await create_engine(
        database=db_config['name'],
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'])


metadata = MetaData()


Operation = Table(
    'operation',
    metadata,
    Column('id', String),
    Column('billing_cycle_id', String),
    Column('worker_id', String),  # link to table 'user'
    Column('description', String),
    Column('debit', Integer),  # списание
    Column('credit', Integer),  # пополнение
    Column('time', DateTime),
    PrimaryKeyConstraint('id', name='operation__id__pkey')
)

# договоримся, что в системе может быть лишь один открытый billing_cycle
BillingCycle = Table(
    'billing_cycle',
    metadata,
    Column('id', DateTime),
    Column('start_date', DateTime),
    Column('end_date', DateTime),  # link to task
    Column('status', Integer),  # opened | closed
    PrimaryKeyConstraint('id', name='operation__id__pkey')
)


Task = Table(
    'task',
    metadata,
    Column('id', String),
    Column('assigned_worker', String),
    Column('assign_price', Integer),
    Column('finish_price', Integer),
    PrimaryKeyConstraint('id', name='task__id__pkey')
)

PersonalBalance = Table(
    'personal_balance',
    metadata,
    Column('user_id', String),
    Column('value', Integer),
    PrimaryKeyConstraint('id', name='personal_account__user_id__pkey')
)

Price = Table(
    'price',
    metadata,
    Column('task_id', String),
    Column('assign_price', Integer),
    Column('finish_price', Integer),
    PrimaryKeyConstraint('id', name='price__task_id__pkey')
)
