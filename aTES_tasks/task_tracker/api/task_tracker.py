"""
Implementation of a service
"""
import logging
from typing import List

from aiohttp_jsonrpc_algont.handler import JSONRPCView
from aiohttp_cors import CorsViewMixin

from m7_aiohttp.auth.access import AccessAioHttp, Unauthorized, Forbidden
from m7_aiohttp.exceptions import NotFound, InvalidParams
from m7_aiohttp.util.jsonrpc_logged import jsonrpc_logged, jsonrpc_class_decorated
from m7_cerberus.m7_validator import validated


from task_tracker.api.exceptions import CustomException
from task_tracker.validation import schemas
from task_tracker.dao.dao_task_tracker import DAOTask


logger = logging.getLogger('task-tracker')


@jsonrpc_class_decorated(jsonrpc_logged(logger))
class TaskTrackerService(CorsViewMixin, JSONRPCView):
    """
    View of a service
    """
    __JSONRPC_EXCEPTIONS__ = {
        Unauthorized: Unauthorized.code,
        Forbidden: Forbidden.code,
        InvalidParams: InvalidParams.code,
        NotFound: NotFound.code,
        CustomException: CustomException.code
    }


    @property
    def _dao(self) -> DAOTask:
        return self.request.app['dao']

    @property
    def _access(self) -> AccessAioHttp:
        return self.request.app['access']

    @validated(schemas.ECHO)
    async def rpc_echo(self, message: str) -> str:
        """
        Sample echo method

        Args:
            message:

        Returns:
            the same message

        """
        self._access.authenticated(self.request)
        return message

    @validated(schemas.GET)
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
        self._access.authenticated(self.request)
        return await self._dao.get(id)

    @validated(schemas.ADD)
    async def rpc_add(self, task: dict) -> str:
        """
        Add task

        Args:
            task:

        Returns:
            id of added entity

        """
        self._access.authenticated(self.request)
        return await self._dao.add(task)

    @validated(schemas.SET)
    async def rpc_set(self, task: dict):
        """
        Change entity

        Args:
            task:

        """
        self._access.authenticated(self.request)
        await self._dao.set(task)

    @validated(schemas.DELETE)
    async def rpc_delete(self, id):
        """
        Delete task

        Args:
            id:

        """
        self._access.authenticated(self.request)
        await self._dao.delete(id)

    @validated(schemas.GET_COUNT_BY_FILTER)
    async def rpc_get_count_by_filter(self, filter: dict) -> int:  # pylint: disable = redefined-builtin
        """
        Get maximum count of items in filtered query

        Args:
            filter: same as in get_list_by_filter

        Returns:
            items count

        """
        self._access.authenticated(self.request)
        return await self._dao.get_count_by_filter(filter)

    @validated(schemas.GET_LIST_BY_FILTER)
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
        self._access.authenticated(self.request)
        return await self._dao.get_list_by_filter(filter, order, limit, offset)





