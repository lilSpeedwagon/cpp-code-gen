from enum import Enum


class ParsingError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def parse_enum(
    value: str, enum, enum_name: str, owner_name: str = ''
) -> Enum:
    for enum_item in enum:
        if value == enum_item.value:
            return enum_item

    raise ParsingError(
        'field {} of item {} has invalid value \'{}\''.format(
            enum_name, owner_name, value
        ) if owner_name else
        '{} has invalid value \'{}\'}'.format(enum_name, value)
    )
