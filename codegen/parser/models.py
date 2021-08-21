from enum import Enum
from typing import List

import codegen.parser.utils as utils


class Keys:
    TYPE = 'type'
    DESCRIPTION = 'description'
    FORMAT = 'format'
    ENUM = 'enum'
    ARR_TYPE = 'array_type'
    ITEMS = 'items'
    PROPERTIES = 'properties'
    REQUIRED = 'required'


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


class ItemRef:
    """
    ItemRef may be a nested ModelItem or
    a reference to other type
    """

    def __init__(self) -> None:
        self.__ref: str = None
        self.__item: ModelItem = None

    def set_ref(self, ref: str) -> None:
        self.__ref = ref
        self.__item = None

    def set_item(self, item: ModelItem) -> None:
        self.__item = item
        self.__ref = None

    def get_item(self) -> ModelItem:
        return self.__item

    def get_ref(self) -> str:
        return self.__ref

    def is_ref(self) -> bool:
        return self.__ref is not None

    def is_item(self) -> bool:
        return self.__item is not None


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
        self.items_type: ItemRef = None

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
        self.items_type = parse_ref_or_nested_item(items_field, self.name)

    @staticmethod
    def get_type() -> ModelItemType:
        return ModelItemType.Array


class ModelObject(ModelItem):
    def __init__(self, name: str) -> None:
        super().__init__(
            name=name,
            allowed_fields=[
                Keys.PROPERTIES,
                Keys.REQUIRED,
            ],
        )
        self.properties: List(ItemRef) = {}
        self.required: List(str) = []

    def parse(self, item_dict: dict) -> None:
        super().parse(item_dict)
        self.__parse_properties(item_dict)
        self.__parse_required(item_dict)

    def __parse_properties(self, item_dict: dict) -> None:
        if Keys.PROPERTIES not in item_dict:
            raise utils.ParsingError(
                msg='field \'{}\' is required'.format(Keys.PROPERTIES),
                context=self.name,
            )

        props_field = item_dict[Keys.PROPERTIES]
        if not props_field or not isinstance(props_field, dict):
            raise utils.ParsingError(
                msg='{} must be a dictionary'.format(Keys.PROPERTIES),
                context=self.name,
            )

        for name, property in props_field.items():
            ref = parse_ref_or_nested_item(property, self.name)
            self.properties[name] = ref

    def __parse_required(self, item_dict: dict) -> None:
        if Keys.REQUIRED not in item_dict:
            return
        required_list = item_dict[Keys.REQUIRED]
        if not required_list:
            return

        error_msg = '\'{}\' must be a list of property names'.format(
            Keys.REQUIRED
        )
        if not isinstance(required_list, list):
            raise utils.ParsingError(msg=error_msg, context=self.name)

        for item in required_list:
            if not isinstance(item, str) or item not in self.properties.keys():
                raise utils.ParsingError(msg=error_msg, context=self.name)
            self.required.append(item)

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


def parse_ref_or_nested_item(field, parent_name: str) -> ItemRef:
    """
    Checks whether the specified field of the object is a reference
    or a nested object and raises an error if it is something else.
    """

    is_reference = utils.is_reference(field)
    if not is_reference and not isinstance(field, dict):
        raise utils.ParsingError(
            msg='{} must be an object or a reference, got {}'.format(
                Keys.ITEMS,
                field,
            ),
            context=parent_name,
        )

    result = ItemRef()
    if is_reference:
        result.set_ref(utils.get_referenced_item_name(field))
    else:
        name = '{}Items'.format(parent_name)
        type = get_item_type(item=field, item_name=name)
        item = create_item(name, type)
        item.parse(field)
        result.set_item(item)

    return result
