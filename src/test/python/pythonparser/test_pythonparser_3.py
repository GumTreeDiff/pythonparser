# Copyright (c) Aniskov N.

import os
from typing import *
from xml.etree import ElementTree as ET

import pytest

from src.main.python.pythonparser.pythonparser_3 import *
from src.main.util.const import TEST_RESOURCES_PATH


class TestPythonParser3:

    _input_dir = os.path.join(TEST_RESOURCES_PATH, 'pythonparser/pythonparser_3')

    test_cases_dirs = \
        [
            os.path.join(_input_dir, 'case_small_code_snippets'),

            os.path.join(_input_dir, 'case_big_code_snippets'),

            os.path.join(_input_dir, 'case_classes'),

            os.path.join(_input_dir, 'case_empty_file'),

            pytest.param(os.path.join(_input_dir, 'case_fstrings'),
                         marks=pytest.mark.skip(reason='fstrings are not supported yet')),

            pytest.param(os.path.join(_input_dir, 'case_python_3_8'),
                         marks=pytest.mark.skip(reason='python 3.8 not supported yet'))
        ]

    # Helper functions:

    @staticmethod
    def __get_xml_tree(path_to_py_file: str) -> ET.Element:
        parsed_json = parse_file(path_to_py_file)
        xml_str = json2xml(parsed_json)
        root = ET.fromstring(xml_str)
        return root

    @staticmethod
    def __get_count_token_occurrence(tree: ET.Element, tokens: Iterable[str]) -> Dict[str, int]:
        return {token: len(tree.findall('.//' + token))
                for token in tokens}

    # Tests:

    @pytest.mark.parametrize(
        'cases_dirs',
        test_cases_dirs
    )
    def test_produce_valid_xml(self, cases_dirs: str) -> None:
        """
        :arg: list of input dirs (pytest parametrize)
        Checks if parser producing valid xml file
        """

        for entry in os.scandir(cases_dirs):
            # print(f'Current entry is: {entry.path}') TODO: remove or add logger instead
            parsed_json = parse_file(entry.path)
            xml_str = json2xml(parsed_json)
            try:
                _ = ET.fromstring(xml_str)
            except ET.ParseError as e:
                pytest.fail(f'test file: {entry.path}, ET.ParseError msg: {e}')

    @pytest.mark.parametrize(
        'test_input_dirs',
        [
            os.path.join(_input_dir, 'case_non_valid_python_code')
        ]
    )
    def test_non_valid_python_code(self, test_input_dirs: str) -> None:
        """
        Checks behaviour on non valid python code inputs.
        Expected behaviour: SyntaxError is thrown during parsing
        """
        for entry in os.scandir(test_input_dirs):
            # print(f'Current entry is: {entry.path}') TODO: remove or add logger instead
            with pytest.raises(SyntaxError):
                _ = parse_file(entry.path)

    @pytest.mark.parametrize(
        'test_input_dirs',
        [
            os.path.join(_input_dir, 'case_non_valid_python_code')
        ]
    )
    def test_non_valid_python_code(self, test_input_dirs: str) -> None:
        """
        Checks behaviour on non valid python code inputs.
        Expected behaviour: SyntaxError is thrown during parsing
        """
        for entry in os.scandir(test_input_dirs):
            # print(f'Current entry is: {entry.path}') TODO: remove or add logger instead
            with pytest.raises(SyntaxError):
                _ = parse_file(entry.path)

    @staticmethod
    @pytest.fixture(scope='function',
                    params=[
                        ({'lineno': '4', 'col': '0', 'end_line_no': '24', 'end_col': '63'}, 'FunctionDef'),
                        ({'lineno': '16', 'col': '18', 'end_line_no': '16', 'end_col': '27'}, 'BinOp_LShift'),
                        ({'lineno': '16', 'col': '18', 'end_line_no': '16', 'end_col': '22'}, 'Subscript_Load')
                    ]
                    )
    def token_params_sample(request) -> Tuple[Dict[str, str], str]:
        return request.param

    def test_correct_token_params(self, token_params_sample) -> None:
        input_file_paths = os.path.join(self._input_dir, 'case_small_code_snippets/small_3.py')
        (expected, xml_element) = token_params_sample
        root = self.__get_xml_tree(input_file_paths)
        match = root.find('.//' + xml_element)
        assert match is not None
        match_params = match.attrib
        result = {key: match_params[key] for key in expected.keys()}
        assert result == expected

    @staticmethod
    @pytest.fixture(scope='function',
                    params=[
                        ({'Assign': 2, 'Call': 2, 'Import': 1, 'FunctionDef': 0},
                         os.path.join(_input_dir, 'case_small_code_snippets/small_2.py')),
                        ({'Assign': 3, 'AugAssign_Add': 1, 'For': 4, 'List_Load': 12},
                         os.path.join(_input_dir, 'case_small_code_snippets/small_4.py')),
                    ]
                    )
    def tokens_to_cnt(request) -> Tuple[Dict[str, int], str]:
        return request.param

    def test_all_tokens_are_accounted_for(self, tokens_to_cnt) -> None:
        """
        Checks that all tokens such as Assign, Call,.. etc
        are accounted for by parser
        """
        (expected, input_file_path) = tokens_to_cnt
        root = self.__get_xml_tree(input_file_path)
        result = self.__get_count_token_occurrence(root, expected.keys())
        assert result == expected

    @staticmethod
    @pytest.fixture(scope='function',
                    params=[
                        ({'Name_Store': 2, 'Name_Load': 4, 'Attribute_Store': 0, 'Attribute_Load': 1},
                         os.path.join(_input_dir, 'case_small_code_snippets/small_2.py')),
                        ({'Name_Store': 5, 'Name_Load': 13, 'Attribute_Store': 0, 'Attribute_Load': 3},
                         os.path.join(_input_dir, 'case_small_code_snippets/small_3.py')),
                    ]
                    )
    def merged_tokens_to_cnt(request) -> Tuple[Dict[str, int], str]:
        return request.param

    def test_merge_expr_context_and_ops_into_type(self, merged_tokens_to_cnt) -> None:
        """
        Checks that parser correctly include expr_context and operators
        into the type instead of creating a child
        """
        (expected, input_file_path) = merged_tokens_to_cnt
        root = self.__get_xml_tree(input_file_path)
        result = self.__get_count_token_occurrence(root, expected.keys())
        assert result == expected



