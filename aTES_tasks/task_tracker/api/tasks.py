"""
Implementation of a service
"""
import json
import logging
from typing import List

from aiohttp_jsonrpc.handler import JSONRPCView
from aiohttp_cors import CorsViewMixin

from task_tracker.api import const
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
    def _dao(self) -> DAOTasks:
        return self.request.app['dao_tasks']

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
    def _status_changed_routing_key(self):
        return self._config['exchanges']['task_status_change']['name']

    @staticmethod
    def _message(obj: dict, event: str):
        return {
            'event': event,
            'object': obj
        }

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
        return await self._dao.get(id)

    async def rpc_add(self, task: dict) -> str:
        """
        Add task

        Args:
            task:

        Returns:
            id of added entity

        """
        task_id = await self._dao.add(task)
        task = await self._dao.get(task_id)
        await self._publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_CREATED))
        )
        return task_id

    async def rpc_set(self, task: dict):
        """
        Change entity

        Args:
            task:

        """
        await self._dao.set(task)
        task = await self._dao.get(task['id'])
        await self._publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(task, const.EVENT__TASK_UPDATED))
        )

    async def rpc_delete(self, id):
        """
        Delete task

        Args:
            id:

        """
        task = await self._dao.get(id)
        await self._dao.delete(id)
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
        return await self._dao.get_count_by_filter(filter)

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
        return await self._dao.get_list_by_filter(filter, order, limit, offset)
