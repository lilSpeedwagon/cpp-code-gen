from typing import Dict

from codegen.models import *


class ParsingError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Parser:
    def __init__(self) -> None:
        self.__model_items: Dict(str, ModelItem) = {}


    def parse(self, yaml_document: dict):
        definitions = self.__get_definitions_block(yaml_document)
        
        for item_name in definitions:
            item_dict = definitions[item_name]
            item = Parser.__parse_item(item_name, item_dict)
            self.__add_item(item)
            Parser.__debug_print_item_info(item)


    def __add_item(self, item: ModelItem):
        if item.name in self.__model_items:
            raise ParsingError('{} is defined more than once'.format(item.name))
        self.__model_items[item.name] = item


    @staticmethod
    def __parse_item(name: str, item_dict: dict) -> ModelItem:
        type = Parser.__get_item_type(item_dict, name)
        item = Parser.__create_item(name, type)
        item.description = Parser.__parse_description(item_dict)

        if item.get_type() == ModelItemType.Int:
            Parser.__parse_int(item_dict, item)

        if item.get_type() == ModelItemType.Number:
            Parser.__parse_number(item_dict, item)

        return item


    @staticmethod
    def __parse_description(item_dict: dict) -> str:
        if Keys.DESCRIPTION in item_dict:
            return item_dict[Keys.DESCRIPTION]
        return None


    @staticmethod
    def __parse_int(item_dict: dict, item: ModelInt) -> None:
        if Keys.FORMAT in item_dict:
            int_type_str = item_dict[Keys.FORMAT]
            item.int_type = Parser.__parse_enum(
                value = int_type_str,
                enum = ModelInt.IntType,
                enum_name = Keys.FORMAT,
                owner_name = item.name,
            )


    @staticmethod
    def __parse_number(item_dict: dict, item: ModelNumber) -> None:
        if Keys.FORMAT in item_dict:
            num_type_str = item_dict[Keys.FORMAT]
            item.number_type = Parser.__parse_enum(
                value = num_type_str,
                enum = ModelNumber.NumberType,
                enum_name = Keys.FORMAT,
                owner_name = item.name,
            )
            

    @staticmethod
    def __create_item(
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


    @staticmethod
    def __get_definitions_block(yaml_document: dict) -> dict:
        definitions_block_name = 'definitions'
        if definitions_block_name not in yaml_document:
            raise ParsingError(
                    'cannot find \'definitions\' block '
                    'in the root of the document'
                )
        return yaml_document[definitions_block_name]


    @staticmethod
    def __get_item_type(item: dict, item_name: str) -> ModelItemType:
        if Keys.TYPE not in item:
            raise ParsingError(
                'field \'type\' is required for item {}'.format(item_name)
            )
        return Parser.__parse_enum(
            value = item[Keys.TYPE],
            enum = ModelItemType,
            enum_name = Keys.TYPE,
            owner_name = item_name,
        )


    @staticmethod
    def __parse_enum(value: str, enum, enum_name: str, owner_name: str = '') -> Enum:
        for enum_item in enum:
            if value == enum_item.value:
                return enum_item

        raise ParsingError(
            'field {} of item {} has invalid value \'{}\''.format(
                enum_name, owner_name, value
            ) if owner_name else
            '{} has invalid value \'{}\'}'.format(enum_name, value)
        )


    @staticmethod
    def __debug_print_item_info(item: ModelItem):
        print(item.__dict__)