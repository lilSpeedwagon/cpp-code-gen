import pytest

from codegen.utils import ParsingError
import codegen.models as models


@pytest.mark.parametrize(
    "item_dict,expected_description,is_err_expected",
    [
        (
            {},
            '',
            False,
        ),
        (
            {'description': 'desc'},
            'desc',
            False,
        ),
        (
            {'description': 1},
            '',
            True,
        ),
        (
            {'field'},
            None,
            True,
        ),
    ],
    ids=['empty', 'with desc', 'bad desc', 'extra field']
)
def test_parse_item(
    item_dict: dict,
    expected_description: str,
    is_err_expected: bool,
):
    name = 'Item'
    item = models.ModelItem(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert expected_description == item.description
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)


@pytest.mark.parametrize(
    "item_dict,expected_type,is_err_expected",
    [
        (
            {},
            models.ModelInt.IntType.Int32,
            False,
        ),
        (
            {'format': 'int32'},
            models.ModelInt.IntType.Int32,
            False,
        ),
        (
            {'format': 'int64'},
            models.ModelInt.IntType.Int64,
            False,
        ),
        (
            {'format': 'int33'},
            None,
            True,
        ),
        (
            {'extra': 'value'},
            None,
            True,
        ),
    ],
    ids=['empty', 'int32', 'int64', 'bad format', 'extra field']
)
def test_parse_int(
    item_dict: dict,
    expected_type: models.ModelInt.IntType,
    is_err_expected: bool,
):
    name = 'Integer'
    item = models.ModelInt(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert expected_type == item.int_type
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)


@pytest.mark.parametrize(
    "item_dict,expected_type,is_err_expected",
    [
        (
            {},
            models.ModelNumber.NumberType.Float,
            False,
        ),
        (
            {'format': 'float'},
            models.ModelNumber.NumberType.Float,
            False,
        ),
        (
            {'format': 'double'},
            models.ModelNumber.NumberType.Double,
            False,
        ),
        (
            {'format': 'int'},
            None,
            True,
        ),
        (
            {'extra': 'value'},
            None,
            True,
        ),
    ],
    ids=['empty', 'float', 'double', 'bad format', 'extra field']
)
def test_parse_number(
    item_dict: dict,
    expected_type: models.ModelNumber.NumberType,
    is_err_expected: bool,
):
    name = 'Integer'
    item = models.ModelNumber(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert expected_type == item.number_type
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)


@pytest.mark.parametrize(
    "item_dict,expected_enum,is_err_expected",
    [
        (
            {},
            [],
            False,
        ),
        (
            {'enum': ['value1', 'value2']},
            ['value1', 'value2'],
            False,
        ),
        (
            {'enum': []},
            [],
            True,
        ),
        (
            {'enum': {}},
            None,
            True,
        ),
        (
            {'enum': [1, 2, 3]},
            None,
            True,
        ),
        (
            {
                'enum': 'value',
                'extra': 'value'
            },
            None,
            True,
        ),
    ],
    ids=[
        'empty', 'enum', 'empty enum', 'bad enum', 'bad enum items', 'extra'
    ]
)
def test_parse_string(
    item_dict: dict,
    expected_enum: list,
    is_err_expected: bool,
):
    name = 'String'
    item = models.ModelString(name)
    assert item.name == name
    try:
        item.parse(item_dict)
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)

    if expected_enum:
        assert expected_enum == item.enum.enum_list
