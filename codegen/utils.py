from enum import Enum


REFERENCE_PREFIX = '#'


class ParsingError(RuntimeError):
    def __init__(self, msg: str, context: str = '') -> None:
        msg = '{}: {}'.format(context, msg) if context else msg
        super().__init__(msg)


def parse_enum(
    value: str, enum, enum_name: str, owner_name: str = ''
) -> Enum:
    for enum_item in enum:
        if value == enum_item.value:
            return enum_item

    raise ParsingError(
        msg='field {} has invalid value \'{}\''.format(
            enum_name, value
        ),
        context=owner_name,
    )

def is_reference(ref) -> bool:
    return isinstance(ref, str) and ref.startswith(REFERENCE_PREFIX)

def get_referenced_item_name(ref: str) -> str:
    return ref.removeprefix(REFERENCE_PREFIX)
        
