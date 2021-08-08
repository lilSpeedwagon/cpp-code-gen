from yaml.scanner import ScannerError

import codegen.yaml_loader as yaml_loader
from codegen.parser import Parser


class CodeGenerator:
    def __init__(self) -> None:
        pass

    def generate_cpp(self, source_file_path: str, result_file_path: str):
        # read YAML
        print('loading file {}...'.format(source_file_path))
        yaml_doc = yaml_loader.load(source_file_path)
        print('done.')

        # parse YAML into intermediate model
        print('parsing schema...')
        parser = Parser()
        data_model = parser.parse(yaml_doc)
        print('done.')

        # write resulting .h/.cpp

        pass
