"""
Manipulate in database with tables
"""
import random
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func

from billing import const
from billing.exceptions import NotFound
from billing.db import Price, Task
from billing.dao.filters import make_string_filter


async def handle_task_data(task, dao_tasks):
    """
    Creates new task if task not exist or updates existent task
    """
    task_id = task[const.ID]
    try:
        await dao_tasks.get(task_id)
        await dao_tasks.set(task)
    except NotFound:
        assign_price = random.randint(10, 20)
        finish_price = random.randint(20, 40)
        task[const.ASSIGN_PRICE] = assign_price
        task[const.FINISH_PRICE] = finish_price
        await dao_tasks.add(task)
        return task


class DAOTasks:
    """
    DAO for 'task' table
    """
    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    async def _add_price(conn, task):
        price = {
            const.TASK_ID: task[const.TASK_ID],
            const.FINISH_PRICE: task[const.FINISH_PRICE],
            const.ASSIGN_PRICE: task[const.ASSIGN_PRICE]
        }
        await conn.execute(Price.insert().values(**price))

    async def _add(self, conn, obj: dict) -> str:
        await conn.execute(
            Task.insert().values(**obj)
        )
        await self._add_price(conn, obj)
        return obj[const.ID]

    async def _set(self, conn, obj: dict) -> None:
        await conn.execute(
            Task.update().values(**obj).
            where(Task.c.id == obj[const.ID])
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
        if const.TASK_NAME in filter_:
            query = query.where(make_string_filter(Task.c.name, filter_[const.TASK_NAME]))
        if const.ID in filter_:
            values = filter_[const.ID]['values']
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

    async def get_not_finished_tasks(self):
        async with self.engine.acquire() as conn:
            # we need to set real limits in future
            filter_ = {
                const.STATUS: {
                    'values': [const.TASK_STATUS__OPENED, const.TASK_STATUS__IN_PROGRESS]
                }
            }
            order = []
            limit = 1000
            offset = 0
            return await self._get_list_by_filter(conn, filter_, order, limit, offset)
