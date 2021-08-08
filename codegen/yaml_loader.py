import yaml
from yaml.constructor import ConstructorError


try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def __no_duplicates_constructor(loader, node, deep=False):
    """
    custom constructor raising errors in case of key duplicating
    """

    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "YAML mapping ",
                node.start_mark,
                "found duplicate key (%s)" % key,
                key_node.start_mark,
            )
        mapping[key] = value

    return loader.construct_mapping(node, deep)


yaml.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    __no_duplicates_constructor,
    Loader=yaml.SafeLoader,
)


def load(source_path: str):
    file = open(source_path, 'r')
    yaml_document = yaml.safe_load(file)
    if not yaml_document:
        raise RuntimeError('No YAML documents found')
    return yaml_document
