# Copyright (c) Aniskov N.

import os

import pytest

from src.main.python.inverse_parser.inverse_parser_3 import *
from src.main.python.pythonparser.pythonparser_3 import json2xml, parse_file
from src.main.util.const import TEST_RESOURCES_PATH


@pytest.mark.skip('Simple equals between code does not work.'
                  'The parser add brackets even if they were not in the source code.')
class TestInverseParser3:

    _input_dir = os.path.join(TEST_RESOURCES_PATH, 'inverse_parser/inverse_parser_3')

    test_cases_dirs = \
        [
            os.path.join(_input_dir, 'case_for'),

            os.path.join(_input_dir, 'case_import'),

            os.path.join(_input_dir, 'case_simple_ops')

        ]

    # Tests:

    @pytest.mark.parametrize(
        'cases_dirs',
        test_cases_dirs
    )
    def test_generated_code_is_eq_to_original(self, cases_dirs: str) -> None:
        for entry in os.scandir(cases_dirs):
            xml_ast_str = json2xml(parse_file(entry.path))
            inverse_parser = InverseParser(xml_ast_str)

            with open(entry.path) as in_f:
                real_source = in_f.read()
            generated_source = inverse_parser.get_source()

            assert real_source == generated_source
