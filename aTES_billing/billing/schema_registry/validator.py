"""
Provides handler for validating certain event messager
"""
import asyncio
import json
import os
from typing import Dict

from cerberus import Validator


class ValidationSchemaNotFound(Exception):
    """
    Raises if validation schema for specified event wasn't found
    """

# потенциально тут нужен класс-загрузчик, который с некоторой периодичностью будет
# осматривать все доступные схемы и загружать их в память сервиса для оперативного доступа


class SchemaRegistryValidator:
    def __init__(
            self,
            schemas_dir_path
    ):
        self.schemas_dir_path = schemas_dir_path

    def _get_schema(self, event, version):
        event_name_with_slashes = event.replace('.', '/')
        schema_path = '{schemas_dir_path}/{event_name_with_slashes}/{version}.json'.format(
            schemas_dir_path=self.schemas_dir_path, event_name_with_slashes=event_name_with_slashes, version=version
        )
        if not os.path.isfile(schema_path):
            raise ValidationSchemaNotFound
        with open(schema_path) as file:
            return json.load(file)

    def validate(self, data: dict, event, version) -> Dict[str, list]:
        """
        Validates data of certain event according to event's version
        """
        schema = self._get_schema(event, version)
        validator = Validator(schema)
        validator.validate(data)
        return validator.errors
