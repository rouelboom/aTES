"""
Implementation of a service
"""
import json
from typing import List

from aiohttp_jsonrpc.handler import JSONRPCView
from aiohttp_cors import CorsViewMixin

from accounts.api import const
from accounts.exceptions import Forbidden, InvalidParams, NotFound, Unauthorized
from accounts.rmq.publisher import RabbitMQPublisher
from accounts.validation import schemas
from accounts.dao.dao_users import DAOUsers


class UsersService(CorsViewMixin, JSONRPCView):
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
    def _dao_users(self) -> DAOUsers:
        return self.request.app['dao_users']

    @property
    def _user_publisher(self) -> RabbitMQPublisher:
        return self.request.app['user_publisher']

    @property
    def _config(self) -> dict:
        return self.request.app['config']

    @property
    def _streaming_routing_key(self):
        return self._config['exchanges']['user_streaming']['name']

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
        Get user by id

        Args:
            id:

        Returns:
            user

        Raises:
            NotFound: (-404)

        """
        return await self._dao_users.get(id)

    async def rpc_sing_up(self, user: dict) -> str:
        """
        Add user

        Args:
            user:

        Returns:
            id of added entity

        """
        self._authenticated()

        errors = schemas.validate_user_info(user, schemas.SIGN_UP)
        if errors:
            raise InvalidParams

        user_id = await self._dao_users.add(user)
        user = await self._dao_users.get(user_id)

        await self._user_publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(user, const.EVENT__USER_CREATED))
        )
        return user_id

    async def rpc_set(self, user: dict):
        """
        Change entity

        Args:
            user:

        """
        self._authenticated()

        errors = schemas.validate_user_info(user, schemas.SET)
        if errors:
            raise InvalidParams

        await self._dao_users.set(user)
        user = await self._dao_users.get(user[const.ID])
        await self._user_publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(user, const.EVENT__USER_UPDATED))
        )

    async def rpc_delete(self, id):
        """
        Delete user

        Args:
            id:

        """
        self._authenticated()
        user = await self._dao_users.get(id)
        await self._dao_users.delete(id)
        await self._user_publisher.publish(
            self._streaming_routing_key,
            json.dumps(self._message(user, const.EVENT__USER_DELETED))
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
        return await self._dao_users.get_count_by_filter(filter)

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
        return await self._dao_users.get_list_by_filter(filter, order, limit, offset)
