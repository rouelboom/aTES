"""
Database objects definitions
"""
import os

from aiopg.sa import create_engine
from sqlalchemy import MetaData, Table, Column, String, PrimaryKeyConstraint
from dotenv import load_dotenv

load_dotenv()

db_host = 'localhost'
db_name = 'task'
credentials_login = 'postgres'
credentials_password = 'postgres'


async def init_engine() -> 'Engine':
    """
    Engine initialization
    """
    return await create_engine(
        database=db_name,
        host=db_host,
        user=credentials_login,
        password=credentials_password)

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
