from enum import Enum
from typing import List

import codegen.utils as utils


class Keys:
    TYPE = 'type'
    DESCRIPTION = 'description'
    FORMAT = 'format'
    ENUM = 'enum'


class ModelItemType(Enum):
    Item = 'item'
    Int = 'int'
    Number = 'number'
    Bool = 'bool'
    String = 'string'
    Array = 'array'
    Object = 'object'


class ModelItem:
    def __init__(self, name: str, allowed_fields: list = []) -> None:
        self.id = ''  # TODO generate some rand value
        self.name: str = name
        self.description: str = ''
        self.__allowed_fields: List[str] = allowed_fields + [
            Keys.TYPE, Keys.DESCRIPTION
        ]

    def parse(self, item_dict: dict) -> None:
        self.__check_allowed_fields(item_dict)
        if Keys.DESCRIPTION in item_dict:
            description = item_dict[Keys.DESCRIPTION]
            if not isinstance(description, str):
                raise utils.ParsingError(
                    '{} description must be a string'.format(self.name)
                )
            self.description = description

    def __check_allowed_fields(self, item_dict: dict) -> None:
        for item in item_dict:
            if item not in self.__allowed_fields:
                raise utils.ParsingError(
                    '{} has unknown field \'{}\''.format(
                        self.name, item
                    )
                )

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Item


class ModelInt(ModelItem):
    class IntType(Enum):
        Uint32 = 'uint32'
        Uint64 = 'uint64'
        Int32 = 'int32'
        Int64 = 'int64'

    def __init__(self, name: str) -> None:
        super().__init__(name, allowed_fields=[Keys.FORMAT])
        self.int_type = ModelInt.IntType.Int32

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        if Keys.FORMAT in item_dict:
            int_type_str = item_dict[Keys.FORMAT]
            self.int_type = utils.parse_enum(
                value=int_type_str,
                enum=ModelInt.IntType,
                enum_name=Keys.FORMAT,
                owner_name=self.name,
            )

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Int


class ModelNumber(ModelItem):
    class NumberType(Enum):
        Float = 'float'
        Double = 'double'

    def __init__(self, name: str) -> None:
        super().__init__(name, allowed_fields=[Keys.FORMAT])
        self.number_type = ModelNumber.NumberType.Float

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        if Keys.FORMAT in item_dict:
            num_type_str = item_dict[Keys.FORMAT]
            self.number_type = utils.parse_enum(
                value=num_type_str,
                enum=ModelNumber.NumberType,
                enum_name=Keys.FORMAT,
                owner_name=self.name,
            )

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Number


class ModelBool(ModelItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Bool


class ModelString(ModelItem):
    class StringEnum:
        def __init__(self, enum_list: List[str]) -> None:
            self.enum_list = enum_list

    def __init__(self, name: str) -> None:
        super().__init__(name, allowed_fields=[Keys.ENUM])
        self.enum: ModelString.StringEnum = None

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        if Keys.ENUM in item_dict:
            self.__parse_enum(item_dict[Keys.ENUM])

    def __parse_enum(self, enum_list: list) -> None:
        if not enum_list:
            raise utils.ParsingError(
                'empty enum in item {}'.format(self.name)
            )

        error_msg = """invalid enum in {},
         must be a list of strings""".format(self.name)
        if not isinstance(enum_list, list):
            raise utils.ParsingError(error_msg)
        for enum_item in enum_list:
            if not isinstance(enum_item, str):
                raise utils.ParsingError(error_msg)
        self.enum = ModelString.StringEnum(enum_list)

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.String


class ModelArray(ModelItem):
    class ArrayType(Enum):
        Array = 'array'
        Set = 'set'

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.item_type: ModelItem = None
        self.array_type = ModelArray.ArrayType.Array

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        # TODO parse arr type

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Array


class ModelObject(ModelItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.properties: List(ModelItem) = []
        self.required: List(ModelItem) = []

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        # TODO parse object properties

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Object
