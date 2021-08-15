from enum import Enum
from typing import List

import codegen.utils as utils


class Keys:
    TYPE = 'type'
    DESCRIPTION = 'description'
    FORMAT = 'format'
    ENUM = 'enum'
    ARR_TYPE = 'array_type'
    ITEMS = 'items'


class ModelItemType(Enum):
    Item = 'item'
    Int = 'int'
    Number = 'number'
    Bool = 'bool'
    String = 'string'
    Array = 'array'
    Object = 'object'


def get_item_type(item: dict, item_name: str) -> ModelItemType:
        if Keys.TYPE not in item:
            raise utils.ParsingError(
                'field \'type\' is required for item {}'.format(item_name)
            )
        return utils.parse_enum(
            value=item[Keys.TYPE],
            enum=ModelItemType,
            enum_name=Keys.TYPE,
            owner_name=item_name,
        )


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
                    msg='description must be a string',
                    context=self.name,
                )
            self.description = description

    def __check_allowed_fields(self, item_dict: dict) -> None:
        for item in item_dict:
            if item not in self.__allowed_fields:
                raise utils.ParsingError(
                    msg='unknown field \'{}\''.format(item),
                    context=self.name,
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
                msg='empty enum',
                context=self.name,
            )

        exception = utils.ParsingError(
            msg='enum must be a list of strings',
            context=self.name,
        )
        if not isinstance(enum_list, list):
            raise exception
        for enum_item in enum_list:
            if not isinstance(enum_item, str):
                raise exception
        self.enum = ModelString.StringEnum(enum_list)

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.String


class ModelArray(ModelItem):
    class ArrayType(Enum):
        Array = 'array'
        Set = 'set'

    def __init__(self, name: str) -> None:
        super().__init__(name, allowed_fields=[
            Keys.ARR_TYPE,
            Keys.ITEMS,
        ])
        self.array_type = ModelArray.ArrayType.Array
        self.items_reference = None
        self.items_type = None

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        self.__parse_items(item_dict)
        if Keys.ARR_TYPE in item_dict:
            arr_type_str = item_dict[Keys.ARR_TYPE]
            self.array_type = utils.parse_enum(
                value=arr_type_str,
                enum=ModelArray.ArrayType,
                enum_name=Keys.ARR_TYPE,
                owner_name=self.name,
            )

    def __parse_items(self, item_dict: dict) -> None:
        if Keys.ITEMS not in item_dict or not item_dict[Keys.ITEMS]:
            raise utils.ParsingError(
                msg='array requires field {}'.format(Keys.ITEMS),
                context=self.name,
            )

        items_field = item_dict[Keys.ITEMS]
        is_reference = utils.is_reference(items_field)
        if not is_reference and not isinstance(items_field, dict):
            raise utils.ParsingError(
                msg='{} must be an object or a reference'.format(Keys.ITEMS),
                context=self.name,
            )

        if is_reference:
            self.items_reference = utils.get_referenced_item_name(items_field)
        else:
            name = '{}Items'.format(self.name)
            type = get_item_type(item=items_field, item_name=self.name)
            item = create_item(name, type)
            item.parse(items_field)
            self.items_type = item


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


def create_item(
        name: str, type: ModelItemType
    ) -> ModelItem:
        types_factory_mapping = {
            ModelInt.get_type():     ModelInt,
            ModelNumber.get_type():  ModelNumber,
            ModelBool.get_type():    ModelBool,
            ModelString.get_type():  ModelString,
            ModelArray.get_type():   ModelArray,
            ModelObject.get_type():  ModelObject,
        }

        if type not in types_factory_mapping:
            raise RuntimeError('unknown type object {}'.format(type))

        item_factory = types_factory_mapping[type]
        return item_factory(name)