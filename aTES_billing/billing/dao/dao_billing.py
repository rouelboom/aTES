"""
Manipulate in database with tables
"""
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func, select

from billing import const
from billing.exceptions import NotFound
from billing.db import Operation, PersonalBalance, BillingCycle
from billing.dao.filters import make_string_filter


class DAOBilling:
    """
    DAO for interaction with 'operation', 'personal_balance' and 'billing_cycle' tables
    """
    def __init__(self, engine):
        self.engine = engine

    async def create_new_billing_cycle(self, start_date, end_date):
        async with self.engine.acquire() as conn:
            async with conn.begin():
                await self._create_new_billing_cycle(conn, start_date, end_date)

    @staticmethod
    async def _create_new_billing_cycle(conn, start_date, end_date):
        billing_cycle = {
            const.ID: uuid.uuid4().hex,
            const.START_DATE: start_date,
            const.END_DATE: end_date,
            const.STATUS: const.STATUS__BILLING_CYCLE__OPENED
        }
        await conn.execute(
            BillingCycle.insert().values(**billing_cycle)
        )

    @staticmethod
    async def _get_current_billing_cycle(conn) -> dict:
        row = await (
            await conn.execute(BillingCycle.select().where(
                BillingCycle.c.status == const.STATUS__BILLING_CYCLE__OPENED)
            )
        ).first()

        if row is None:
            raise NotFound()
        return dict(row)

    async def get_current_billing_cycle(self) -> dict:
        async with self.engine.acquire() as conn:
            return await self._get_current_billing_cycle(conn)

    async def get_billing_cycle(self, billing_cycle_id: str) -> dict:
        async with self.engine.acquire() as conn:
            return await self._get_billing_cycle(conn, billing_cycle_id)

    @staticmethod
    async def _get_billing_cycle(conn, billing_cycle_id: str) -> dict:
        row = await (
            await conn.execute(BillingCycle.select().where(BillingCycle.c.id == billing_cycle_id))
        ).first()

        if row is None:
            raise NotFound()
        return dict(row)

    async def close_billing_cycle(self, billing_cycle_id: str):
        async with self.engine.acquire() as conn:
            async with conn.begin():
                await self._close_billing_cycle(conn, billing_cycle_id)

    async def _close_billing_cycle(self, conn, billing_cycle_id: str):
        billing_cycle = await self._get_billing_cycle(conn, billing_cycle_id)
        billing_cycle[const.STATUS] = const.STATUS__BILLING_CYCLE__CLOSED
        await conn.execute(
            BillingCycle.update().values(**billing_cycle).
            where(BillingCycle.c.id == billing_cycle_id)
        )

    @staticmethod
    async def _set_personal_balance(conn, user_id: str, value: int):
        await conn.execute(
            PersonalBalance.update().values(**{
                const.USER_ID: user_id,
                const.VALUE: value
            }).where(
                PersonalBalance.c.user_id == user_id
            )
        )

    @staticmethod
    async def _get_personal_balance(conn, user_id: str) -> int:
        personal_balance = await (
            await conn.execute(PersonalBalance.select().where(PersonalBalance.c.user_id == user_id))
        ).first()

        if personal_balance is None:
            raise NotFound()
        return personal_balance.value

    @staticmethod
    def _update_balance_value(operation: dict, balance: int):
        debit = operation[const.DEBIT]
        if debit:
            balance -= debit
        credit = operation[const.CREDIT]
        if credit:
            balance += credit
        return balance

    async def _add(self, conn, operation: dict) -> str:
        balance = await self._get_personal_balance(conn, operation[const.WORKER_ID])

        if const.ID not in operation:
            operation[const.ID] = uuid.uuid4().hex
        await conn.execute(
            Operation.insert().values(**operation)
        )

        balance = self._update_balance_value(operation, balance)
        await self._set_personal_balance(conn, operation[const.WORKER_ID], balance)
        return operation[const.ID]

    async def _delete(self, conn, object_id: str):
        await conn.execute(Operation.delete().where(Operation.c.id == object_id))

    async def _get(self, conn, object_id: str):
        row = await (
            await conn.execute(Operation.select().where(Operation.c.id == object_id))
        ).first()

        if row is None:
            raise NotFound()
        return dict(row)

    def _filtered_query(self, query, filter_: dict):
        if const.TASK_NAME in filter_:
            query = query.where(make_string_filter(Operation.c.name, filter_[const.TASK_NAME]))
        for filtering_filed in filter_:
            if filtering_filed in (const.ID, const.WORKER_ID):
                values = filter_[filtering_filed]['values']
                query = query.where(Operation.c[filtering_filed].in_(values))
        if const.ID in filter_:
            values = filter_[const.ID]['values']
            query = query.where(Operation.c.id.in_(values))
        return query

    @staticmethod
    def _ordered_query(query, filter_: List[dict]):
        if not filter_:
            return query.order_by(Operation.c.name)
        for item in filter_:
            field_name = item['field']
            direction = item.get('direction', 'asc')
            if direction == 'asc':
                query = query.order_by(Operation.c[field_name])
            else:
                query = query.order_by(Operation.c[field_name].desc())
        return query

    async def _get_count_by_filter(self, conn, filter_: dict) -> int:
        query = sqlalchemy.select([func.count(Operation.c.id)])
        query = self._filtered_query(query, filter_)
        return await conn.scalar(query)

    async def _get_list_by_filter(self, conn, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        query = Operation.select()
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

    def _filtered_billing_cycle_query(self, query, filter_: dict):
        for filtering_filed in filter_:
            if filtering_filed in (const.STATUS, const.START_DATE, const.END_DATE):
                values = filter_[filtering_filed]['values']
                query = query.where(BillingCycle.c[filtering_filed].in_(values))
        if const.ID in filter_:
            values = filter_[const.ID]['values']
            query = query.where(BillingCycle.c.id.in_(values))
        return query

    @staticmethod
    def _ordered_billing_cycle_query(query, filter_: List[dict]):
        if not filter_:
            return query.order_by(BillingCycle.c.start_date)
        for item in filter_:
            field_name = item['field']
            direction = item.get('direction', 'asc')
            if direction == 'asc':
                query = query.order_by(BillingCycle.c[field_name])
            else:
                query = query.order_by(BillingCycle.c[field_name].desc())
        return query

    async def get_billing_cycle_count_by_filter(self, filter_: dict) -> int:
        async with self.engine.acquire() as conn:
            return await self._get_billing_cycle_count_by_filter(conn, filter_)

    async def get_billing_cycle_list_by_filter(self, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        async with self.engine.acquire() as conn:
            return await self._get_billing_cycle_list_by_filter(conn, filter_, order, limit, offset)

    async def _get_billing_cycle_count_by_filter(self, conn, filter_: dict) -> int:
        query = sqlalchemy.select([func.count(BillingCycle.c.id)])
        query = self._filtered_query(query, filter_)
        return await conn.scalar(query)

    async def _get_billing_cycle_list_by_filter(self, conn, filter_: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
        query = BillingCycle.select()
        query = self._filtered_query(query, filter_)
        query = self._ordered_query(query, order)
        query = query.limit(limit)
        query = query.offset(offset)

        result = []
        async for row in conn.execute(query):
            result.append(dict(row))
        return result
