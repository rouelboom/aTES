"""
Database objects definitions
"""
from aiopg.sa import create_engine
from sqlalchemy import MetaData, Table, Column, String, PrimaryKeyConstraint


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


Task = Table(
    'task',
    metadata,
    Column('id', String),
    Column('name', String),
    Column('description', String),
    Column('assigned_worker', String),  # link to table 'user'
    Column('status', String),
    PrimaryKeyConstraint('id', name='task__id__pkey')
)

User = Table(
    'user',
    metadata,
    Column('id', String),
    Column('role', String),
    Column('login', String),
    PrimaryKeyConstraint('id', name='user__id__pkey')
)
