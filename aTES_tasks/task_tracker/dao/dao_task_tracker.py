"""
Manipulate in database with Entity of Scaffolded application
"""
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func

from m7_aiohttp.exceptions import NotFound






from task_tracker.api import const
from task_tracker.db import Task
from task_tracker.dao.filters import make_string_filter


class DAOTask:
    """
    DAO for Entity of Scaffolded application
    """
    def __init__(self, engine):
        self.engine = engine

    async def _add(self, conn, obj: dict) -> str:
        if const.TASK_ID not in obj:
            obj[const.TASK_ID] = uuid.uuid4().hex
        await conn.execute(
            Task.insert().values(**obj)
        )
        return obj[const.TASK_ID]

    async def _set(self, conn, obj: dict) -> None:
        await conn.execute(
            Task.update().values(**obj).
            where(Task.c.id == obj[const.TASK_ID])
        )

    async def _delete(self, conn, object_id: str):
        await conn.execute(Task.delete().where(Task.c.id == object_id))

    async def _get(self, conn, object_id: str):
        row = await (
            await conn.execute(Task.select().where(Task.c.id == object_id))
        ).first()

        if row is None:
            raise NotFound()
        return dict(row)

    def _filtered_query(self, query, filter_: dict):


        if const.SIMPLE_FILTER in filter_:
            query_string = filter_[const.SIMPLE_FILTER][const.SIMPLE_FILTER_QUERY]
            if query_string:
                query = query.where(Task.c.name.ilike('%' + query_string + '%'))
        if const.TASK_NAME in filter_:
            query = query.where(make_string_filter(Task.c.name, filter_[const.TASK_NAME]))
        if const.TASK_ID in filter_:
            values = filter_[const.TASK_ID]['values']
            query = query.where(Task.c.id.in_(values))
        return query

    @staticmethod
    def _ordered_query(query, filter_: List[dict]):
        if not filter_:
            return query.order_by(Task.c.name)
        for item in filter_:
            field_name = item['field']
            direction = item.get('direction', 'asc')
            if direction == 'asc':
                query = query.order_by(Task.c[field_name])
            else:
                query = query.order_by(Task.c[field_name].desc())
        return query

    async def _get_count_by_filter(self, conn, filter_: dict) -> int:
        query = sqlalchemy.select([func.count(Task.c.id)])
        query = self._filtered_query(query, filter_)
        return await conn.scalar(query)

    async def _get_list_by_filter(self, conn, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        query = Task.select()
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
