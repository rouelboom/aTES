"""
Implementation of a service
"""
from typing import List

from aiohttp_jsonrpc.handler import JSONRPCView
from aiohttp_cors import CorsViewMixin

from analytics.dao.dao_users import DAOUsers
from analytics.exceptions import Forbidden, InvalidParams, NotFound, Unauthorized
from analytics.schema_registry.validator import SchemaRegistryValidator
from analytics.utils import get_default_message_data
from analytics.dao.dao_tasks import DAOTasks


class AnalyticsService(CorsViewMixin, JSONRPCView):
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
    def _config(self) -> dict:
        return self.request.app['config']

    @property
    def _streaming_routing_key(self):
        return self._config['exchanges']['task_streaming']['name']

    @property
    def schema_validator(self) -> SchemaRegistryValidator:
        return self.request.app['schema_validator']

    @property
    def _workflow_routing_key(self):
        return self._config['exchanges']['workflow']['name']

    def _message(self, obj: dict, event_name: str):
        errors = self.schema_validator.validate(obj, event_name)
        return {
            **get_default_message_data(version=1),
            'event_name': event_name,
            'data': obj,
        }

    def _authenticated(self):
        """
        Raises
        """
        # в теории, тут надо вернуть токен. из которого можно будет получить идентификатор пользователя
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
