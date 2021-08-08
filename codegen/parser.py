from typing import Dict

import codegen.utils as utils
from codegen.models import *


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
            raise utils.ParsingError(
                '{} is defined more than once'.format(item.name)
            )
        self.__model_items[item.name] = item

    @staticmethod
    def __parse_item(name: str, item_dict: dict) -> ModelItem:
        type = Parser.__get_item_type(item_dict, name)
        item = Parser.__create_item(name, type)
        item.parse(item_dict)
        return item

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
            raise utils.ParsingError(
                    'cannot find \'definitions\' block '
                    'in the root of the document'
                )
        return yaml_document[definitions_block_name]

    @staticmethod
    def __get_item_type(item: dict, item_name: str) -> ModelItemType:
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

    @staticmethod
    def __debug_print_item_info(item: ModelItem):
        print(item.__dict__)
