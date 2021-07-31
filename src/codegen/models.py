from enum import Enum
from typing import List


class ModelItemType(Enum):
    Item = 'item'
    Int = 'int'
    Number = 'number'
    Bool = 'bool'
    String = 'string'
    Array = 'array'
    Object = 'object'


class ModelItem:
    def __init__(self, name: str) -> None:
        self.id = '' # TODO generate some rand value
        self.name = name
        self.description = ''
    
    def get_type() -> ModelItemType:
        return ModelItemType.Item


class ModelInt(ModelItem):
    class IntType(Enum):
        Uint32 = 'uint32'
        Uint64 = 'uint64'
        Int32 = 'int32'
        Int64 = 'int64'

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.int_type = ModelInt.IntType.Int32

    def get_type() -> ModelItemType:
        return ModelItemType.Int


class ModelNumber(ModelItem):
    class NumberType(Enum):
        Float = 'float'
        Double = 'double'

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.number_type = ModelNumber.NumberType.Float
    
    def get_type() -> ModelItemType:
        return ModelItemType.Number


class ModelBool(ModelItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_type() -> ModelItemType:
        return ModelItemType.Bool


class ModelString(ModelItem):
    class StringEnum:
        def __init__(self, enum_list: List[str]) -> None:
            self.enum_list = enum_list

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.enum: ModelString.StringEnum = None
    
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

    def get_type() -> ModelItemType:
        return ModelItemType.Array


class ModelObject(ModelItem):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.properties: List(ModelItem) = []
        self.required: List(ModelItem) = []
        
    def get_type() -> ModelItemType:
        return ModelItemType.Object


class Keys:
    TYPE        = 'type'
    DESCRIPTION = 'description'