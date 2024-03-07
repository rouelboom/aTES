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
    Column('source_id', String),  # link to task
    Column('price', Integer),
    Column('worker_id', String),  # link to table 'user'
    Column('time', DateTime),
    PrimaryKeyConstraint('id', name='operation__id__pkey')
)


Task = Table(
    'task',
    metadata,
    Column('id', String),
    Column('name', String),
    Column('description', String),
    Column('assigned_worker', String),
    Column('price', Integer),
    PrimaryKeyConstraint('id', name='task__id__pkey')
)

CompanyIncome = Table(
    'company_income',
    metadata,
    Column('id', String),
    Column('value', Integer),
    PrimaryKeyConstraint('id', name='company_income__id__pkey')
)

PersonalAccount = Table(
    'personal_account',
    Column('id', String),
    Column('owner_id', String),
    Column('value', Integer),
    PrimaryKeyConstraint('id', name='personal_account__id__pkey')
)
