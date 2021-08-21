from typing import Dict

import codegen.parser.utils as utils
from codegen.parser.models import *


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
        type = get_item_type(item_dict, name)
        item = create_item(name, type)
        item.parse(item_dict)
        return item

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
    def __debug_print_item_info(item: ModelItem):
        print(item.__dict__)
