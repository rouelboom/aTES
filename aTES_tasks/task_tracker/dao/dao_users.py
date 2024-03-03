"""
Manipulate in database with Entity of Scaffolded application
"""
import random
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func

from task_tracker.api import const
from task_tracker.exceptions import NotFound
from task_tracker.db import User
from task_tracker.dao.filters import make_string_filter


class DAOUsers:
    """
    DAO for 'task' table
    """
    def __init__(self, engine):
        self.engine = engine

    async def _add(self, conn, obj: dict) -> str:
        if const.ID not in obj:
            obj[const.ID] = uuid.uuid4().hex
        await conn.execute(
            User.insert().values(**obj)
        )
        return obj[const.ID]

    async def _set(self, conn, obj: dict) -> None:
        await conn.execute(
            User.update().values(**obj).
            where(User.c.id == obj[const.ID])
        )

    async def _delete(self, conn, object_id: str):
        await conn.execute(User.delete().where(User.c.id == object_id))

    async def _get(self, conn, object_id: str):
        row = await (
            await conn.execute(User.select().where(User.c.id == object_id))
        ).first()

        if row is None:
            raise NotFound()
        return dict(row)

    def _filtered_query(self, query, filter_: dict):
        if const.TASK_NAME in filter_:
            query = query.where(make_string_filter(User.c.name, filter_[const.TASK_NAME]))
        if const.ID in filter_:
            values = filter_[const.ID]['values']
            query = query.where(User.c.id.in_(values))
        return query

    @staticmethod
    def _ordered_query(query, filter_: List[dict]):
        if not filter_:
            return query.order_by(User.c.name)
        for item in filter_:
            field_name = item['field']
            direction = item.get('direction', 'asc')
            if direction == 'asc':
                query = query.order_by(User.c[field_name])
            else:
                query = query.order_by(User.c[field_name].desc())
        return query

    async def _get_count_by_filter(self, conn, filter_: dict) -> int:
        query = sqlalchemy.select([func.count(User.c.id)])
        query = self._filtered_query(query, filter_)
        return await conn.scalar(query)

    async def _get_list_by_filter(self, conn, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        query = User.select()
        query = self._filtered_query(query, filter_)
        query = self._ordered_query(query, order)
        query = query.limit(limit)
        query = query.offset(offset)

        result = []
        async for row in conn.execute(query):
            result.append(dict(row))
        return result

    async def add(self, obj: dict) -> str:
        async with self.engine.acquire() as conn:
            async with conn.begin():
                return await self._add(conn, obj)

    async def set(self, obj: dict):
        async with self.engine.acquire() as conn:
            async with conn.begin():
                await self._set(conn, obj)

    async def delete(self, object_id: str):
        async with self.engine.acquire() as conn:
            async with conn.begin():
                await self._delete(conn, object_id)

    async def get(self, object_id: str) -> dict:
        async with self.engine.acquire() as conn:
            return await self._get(conn, object_id)

    async def get_count_by_filter(self, filter_: dict) -> int:
        async with self.engine.acquire() as conn:
            return await self._get_count_by_filter(conn, filter_)

    async def get_list_by_filter(self, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        async with self.engine.acquire() as conn:
            return await self._get_list_by_filter(conn, filter_, order, limit, offset)

    async def get_all_workers(self):
        async with self.engine.acquire() as conn:
            # we need to set real limits in future
            filter_ = {
                const.ROLE: {
                    'values': [const.USER_ROLE__WORKER, ]
                }
            }
            order = []
            limit = 1000
            offset = 0
            return await self._get_list_by_filter(conn, filter_, order, limit, offset)

    async def get_random_user_id(self) -> dict:
        async with self.engine.acquire() as conn:
            # now its request that gets all users from table
            # in future we need to set limits
            filter_ = {}  # means that there are no filtration (return all users)
            order = []
            limit = 1000
            offset = 0
            all_users = await self._get_list_by_filter(conn, filter_, order, limit, offset)
            if not all_users:
                raise NotFound
            users_count = len(all_users)
            user_index = random.randint(0, users_count - 1)
            return all_users[user_index]
