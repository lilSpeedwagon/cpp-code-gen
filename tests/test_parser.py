import pytest

from codegen.utils import ParsingError
import codegen.models as models


def get_item_ref(item: dict, ref: str):
    result = models.ItemRef()
    if item:
        result.set_item(item)
    elif ref:
        result.set_ref(ref)
    return result


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
        assert not is_err_expected
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)

    if expected_description:
        assert expected_description == item.description


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
        assert not is_err_expected
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)

    if expected_type:
        assert expected_type == item.int_type


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
    name = 'Number'
    item = models.ModelNumber(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert not is_err_expected
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)

    if expected_type:
        assert expected_type == item.number_type


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
        assert not is_err_expected
    except ParsingError as e:
        assert is_err_expected, 'unexpected exception: {}'.format(e)

    if expected_enum:
        assert expected_enum == item.enum.enum_list


@pytest.mark.parametrize(
    "item_dict,exp_type,exp_items,exp_ref,is_err_exp",
    [
        (
            {},
            None,
            None,
            None,
            True,
        ),
        (
            {'items': '#ItemRef'},
            models.ModelArray.ArrayType.Array,
            None,
            'ItemRef',
            False,
        ),
        (
            {'items': 'ItemRef'},
            None,
            None,
            None,
            True,
        ),
        (
            {'items': {'type': 'int'}},
            models.ModelArray.ArrayType.Array,
            models.ModelInt('ArrayItems'),
            None,
            False,
        ),
        (
            {'items': '#ItemRef', 'array_type': 'set'},
            models.ModelArray.ArrayType.Set,
            None,
            'ItemRef',
            False,
        ),
        (
            {'items': '#ItemRef', 'extra_field': 'value'},
            None,
            None,
            None,
            True,
        ),
    ],
    ids=[
        'empty', 'ref', 'bad ref', 'int items', 'set', 'extra'
    ]
)
def test_parse_array(
    item_dict: dict,
    exp_type: models.ModelArray.ArrayType,
    exp_items: models.ModelItem,
    exp_ref: str,
    is_err_exp: bool,
):
    name = 'Array'
    item = models.ModelArray(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert not is_err_exp
    except ParsingError as e:
        assert is_err_exp, 'unexpected exception: {}'.format(e)

    if exp_type:
        assert exp_type == item.array_type

    if exp_items:
        assert item.items_type.is_item()
        assert not item.items_type.is_ref()
        assert exp_items.__dict__ == item.items_type.get_item().__dict__

    if exp_ref:
        assert not item.items_type.is_item()
        assert item.items_type.is_ref()
        assert exp_ref == item.items_type.get_ref()


@pytest.mark.parametrize(
    "item_dict,exp_properties,exp_required,is_err_exp",
    [
        (
            {},
            {},
            [],
            True,
        ),
        (
            {'properties': {}},
            {},
            [],
            True,
        ),
        (
            {
                'properties': {'key': 'value'},
            },
            {},
            [],
            True,
        ),
        (
            {
                'properties': {'key': 'value'},
                'required': [],
            },
            {},
            [],
            True,
        ),
        (
            {
                'properties': {'key': '#value'},
                'required': [],
            },
            {
                'key': get_item_ref(None, 'value')
            },
            [],
            False,
        ),
        (
            {
                'properties': {'int_type': {'type': 'int'}},
                'required': [],
            },
            {
                'int_type': get_item_ref(
                    models.ModelInt('ObjectItems'),
                    None,
                )
            },
            [],
            False,
        ),
        (
            {
                'properties': {'int_type': {'type': 'int'}},
                'required': ['extra'],
            },
            {
                'int_type': get_item_ref(
                    models.ModelInt('ObjectItems'),
                    None,
                )
            },
            [],
            True,
        ),
        (
            {
                'properties': {'int_type': {'type': 'int'}},
                'required': ['int_type'],
            },
            {
                'int_type': get_item_ref(
                    models.ModelInt('ObjectItems'),
                    None,
                )
            },
            ['int_type'],
            False,
        ),
    ],
    ids=[
        'no props', 'empty props', 'no req', 'bad ref', 'with ref',
        'with object', 'missing required', 'with required'
    ]
)
def test_parse_object(
    item_dict: dict,
    exp_properties: list,
    exp_required: list,
    is_err_exp: bool,
):
    name = 'Object'
    item = models.ModelObject(name)
    assert item.name == name
    try:
        item.parse(item_dict)
        assert not is_err_exp
    except ParsingError as e:
        assert is_err_exp, 'unexpected exception: {}'.format(e)

    assert len(exp_properties) == len(item.properties)
    for key, value in exp_properties.items():
        assert key in item.properties
        prop = item.properties[key]
        if value.is_ref():
            assert prop.is_ref()
            assert prop.get_ref() == value.get_ref()
        else:
            assert prop.is_item()
            assert prop.get_item().__dict__ == value.get_item().__dict__

    assert len(exp_required) == len(item.required)
    for i in range(len(exp_required)):
        exp_required[i] == item.required[i]