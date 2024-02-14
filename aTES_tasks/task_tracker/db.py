"""
Database objects definitions
"""
from aiopg.sa import create_engine
from m7_data_obfuscator import load_credentials_file
from sqlalchemy import MetaData, Table, Column, String, PrimaryKeyConstraint


async def init_engine(props: dict) -> 'Engine':
    """
    Engine initialization
    """
    assert 'name' in props
    assert 'host' in props
    assert 'credentials_file' in props
    credentials = load_credentials_file(props['credentials_file'])
    return await create_engine(
        database=props['name'],
        host=props['host'],
        user=credentials['login'],
        password=credentials['password'])

metadata = MetaData()

# TODO define your table definitions here

Task = Table(
    'task',
    metadata,
    Column('id', String),
    Column('name', String),
    PrimaryKeyConstraint('id', name='task__id__pkey')
)
