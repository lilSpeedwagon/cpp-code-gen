import yaml


def load(source_path:str):
    file = open(source_path, 'r')
    yaml_document = yaml.safe_load(file)
    if not yaml_document:
        raise RuntimeError('No YAML documents found')
    return yaml_document