"""
Implementation of a service
"""
import json
import logging
from typing import List

from aiohttp_jsonrpc.handler import JSONRPCView
from aiohttp_cors import CorsViewMixin

from task_tracker.api import const
from task_tracker.dao.dao_users import DAOUsers
from task_tracker.exceptions import Forbidden, InvalidParams, NotFound, Unauthorized
from task_tracker.rmq.publisher import RabbitMQPublisher
from task_tracker.validation import schemas
from task_tracker.dao.dao_tasks import DAOTasks


class TaskTrackerService(CorsViewMixin, JSONRPCView):
    """
    View of a service
    """
    __JSONRPC_EXCEPTIONS__ = {
        Unauthorized: Unauthorized.code,
        Forbidden: Forbidden.code,
        InvalidParams: InvalidParams.code,
        NotFound: NotFound.code,
    }

    @property
    def _dao_tasks(self) -> DAOTasks:
        return self.request.app['dao_tasks']

    @property
    def _dao_users(self) -> DAOUsers:
        return self.request.app['dao_users']

    @property
    def _publisher(self) -> RabbitMQPublisher:
        return self.request.app['task_publisher']

    @property
    def _config(self) -> dict:
        return self.request.app['config']

    @property
    def _streaming_routing_key(self):
        return self._config['exchanges']['task_streaming']['name']

    @property
    def _task_status_changed_routing_key(self):
        return self._config['exchanges']['task_status_change']['name']

    @staticmethod
    def _message(obj: dict, event: str):
        return {
            'event': event,
            'object': obj
        }

    def _authenticated(self):
        """
        Raises
        """
        # todo write it after finishing accounts service
        if False:
            raise Exception
        # return token_payload

    async def rpc_echo(self, message: str) -> str:
        """
        Sample echo method

        Args:
            message:

        Returns:
            the same message

        """
        return message

    async def rpc_get(self, id: str) -> dict:
        """
        Get task by id

        Args:
            id:

        Returns:
            task

        Raises:
            NotFound: (-404)

        """
        return await self._dao_tasks.get(id)

    async def rpc_add(self, task: dict) -> str:
        """
        Add task

        Args:
            task:

        Returns:
            id of added entity

        """
        self._authenticated()

        errors = schemas.validate_task(task, schemas.ADD)
        if errors:
            raise InvalidParams

        task_id = await self._dao_tasks.add(task)
        task = await self._dao_tasks.get(task_id)
        try:
            assigned_worker_id = await self._dao_users.get_random_user_id()
        except NotFound as e:
            print('User for task not found')
            raise NotFound from e
        task = {
            **task,
            const.ASSIGNED_WORKER: assigned_worker_id,
            const.STATUS: const.TASK_STATUS__IN_PROGRESS
        }
        await self._publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_CREATED))
        )
        await self._publisher.publish(
            self._task_status_changed_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_CREATED))
        )
        return task_id

    async def rpc_set(self, task: dict):
        """
        Change entity

        Args:
            task:

        """
        self._authenticated()

        errors = schemas.validate_task(task, schemas.SET)
        if errors:
            raise InvalidParams

        await self._dao_tasks.set(task)
        task = await self._dao_tasks.get(task[const.ID])
        await self._publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_UPDATED))
        )

    async def rpc_task_finished(self, task_id: str):
        """
        Set task's status to 'finished'

        Args:
            task_id: ID of task

        """
        self._authenticated()
        # token_payload = self._authenticated()
        # в теории, тут надо из токена получить id пользователя и сравнить его с
        # id работника, на которого назначена задача
        task = await self._dao_tasks.get(task_id)
        # user_id = token_payload['user_id']
        # if user_id != const.USER_ROLE__ADMIN and user_id != task[const.ASSIGNED_WORKER]:
        #     raise Forbidden

        await self._dao_tasks.set(
            {
                const.ID: task_id,
                const.STATUS: const.TASK_STATUS__FINISHED
            }
        )
        await self._publisher.publish(
            self._task_status_changed_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_UPDATED))
        )

    async def rpc_delete(self, id):
        """
        Delete task

        Args:
            id:

        """
        self._authenticated()
        task = await self._dao_tasks.get(id)
        await self._dao_tasks.delete(id)
        await self._publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_DELETED))
        )

    # @validated(schemas.GET_COUNT_BY_FILTER)
    async def rpc_get_count_by_filter(self, filter: dict) -> int:  # pylint: disable = redefined-builtin
        """
        Get maximum count of items in filtered query

        Args:
            filter: same as in get_list_by_filter

        Returns:
            items count

        """
        self._authenticated()
        return await self._dao_tasks.get_count_by_filter(filter)

    # @validated(schemas.GET_LIST_BY_FILTER)
    async def rpc_get_list_by_filter(self,
                                     filter: dict,  # pylint: disable = redefined-builtin
                                     order: List[dict],
                                     limit: int,
                                     offset: int) -> List[dict]:
        """
        Get items by filter

        Args:
            filter: filter
                {
                    "sample_name": {
                        "like": "...",
                        "ilike": "...",
                        "values": ["value 1", ...]
                    }
                }
            order: list of dicts
                [
                    {
                        "field_name": "...",
                        "direction": "asc or desc"
                    },
                    ...
                ]
            limit: maximum count of items
            offset: offset from the beginning of the query

        Returns:
            List of dicts with entities

        """
        self._authenticated()
        return await self._dao_tasks.get_list_by_filter(filter, order, limit, offset)
