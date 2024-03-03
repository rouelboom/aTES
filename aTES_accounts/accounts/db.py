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

User = Table(
    'user',
    metadata,
    Column('id', String),
    Column('role', String),
    Column('login', String),
    Column('beak_shape', String),
    PrimaryKeyConstraint('id', name='user__id__pkey')
)
