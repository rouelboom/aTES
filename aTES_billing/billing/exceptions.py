"""
Basic user exceptions for JSON-RPC methods
"""


class Unauthorized(Exception):
    """
    User is not authorized
    """
    code = -401


class Forbidden(Exception):
    """
    User is authorized but he doesn't have enough right
    """
    code = -403


class NotFound(Exception):
    """
    Raises when requested object not found
    """
    code = -404


class InvalidParams(Exception):
    """
    Raises when incorrect data was passed to JSON-RPC method arguments
    """
    code = -400


class AlreadyExists(Exception):
    """
    Raises when try to add object, which exists already,
    or change unique property to value, which already exists in another object.
    """
    code = -405


class DeleteNotAvailable(Exception):
    """
    Raises when try to delete object, but it's not available at the moment.
    For example, when try to delete object, but there are other objects, which refer to it.
    """
    code = -406
