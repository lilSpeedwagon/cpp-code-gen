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
            self.__model_items[item_name] = item


    @staticmethod
    def __parse_item(name: str, item_dict: dict) -> ModelItem:
        type = Parser.__get_item_type(item_dict, name)
        item = Parser.__create_item(name, type)
        item.description = Parser.__parse_description(item_dict)

        print('{} {} {}'.format(item, item.name, item.description))


    @staticmethod
    def __parse_description(item_dict: dict) -> str:
        if Keys.DESCRIPTION in item_dict:
            return item_dict[Keys.DESCRIPTION]
        return None


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
                'cannot define the type of item {}'.format(item_name)
            )
        return Parser.__parse_type(item[Keys.TYPE])


    @staticmethod
    def __parse_type(type_name: str) -> ModelItemType:
        for type in ModelItemType:
            if type_name == type.value:
                return type
        raise ParsingError('unknown type \'{}\''.format(type_name))
    

    
