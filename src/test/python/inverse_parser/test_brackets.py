# Copyright (c) Aniskov N., Birillo A.

import os
import logging
from typing import List, Optional
from subprocess import check_output, CalledProcessError

import pytest

from src.main.util.const import TEST_RESOURCES_PATH, LOGGER_NAME
from src.test.python.inverse_parser.util import InverseParserTestsUtil
from src.main.util.file_util import get_all_file_system_items, create_file, remove_file, get_content_from_file

log = logging.getLogger(LOGGER_NAME)


# The class provides tests to check the correctness of the brackets
# The parser add brackets even if they were not in the source code
# For example: a = 5 / 10 -> a = (5 / 10)
class TestBrackets:
    EXPRESSIONS_SOURCES_PATH = os.path.join(TEST_RESOURCES_PATH, 'inverse_parser', 'inverse_parser_3', 'brackets')
    EXPRESSIONS_SOURCES = get_all_file_system_items(EXPRESSIONS_SOURCES_PATH)

    @staticmethod
    def __calculate_expression_safely(popen_args: List[str], input: str = '') -> Optional[str]:
        try:
            out = check_output(popen_args, input=input, universal_newlines=True)
            return out.rstrip('\n')
        except CalledProcessError:
            return None

    @staticmethod
    def __get_python_popen_args(py_file_path: str) -> List[str]:
        return ['python3', py_file_path]

    def __get_actual_out(self, source: str) -> Optional[str]:
        parsed_code = InverseParserTestsUtil.source_to_xml_to_source(source)
        log.info(f'Parsed code is:\n{parsed_code}')
        source_file = self.__create_source_file(parsed_code)
        actual_out = self.__calculate_expression_safely(self.__get_python_popen_args(source_file))
        remove_file(source_file)
        return actual_out

    def __create_source_file(self, source_code: str) -> str:
        source_code_file = os.path.join(self.EXPRESSIONS_SOURCES_PATH, 'brackets_test.py')
        create_file(source_code, source_code_file)
        return source_code_file

    @pytest.mark.parametrize('source', EXPRESSIONS_SOURCES)
    def test_expressions(self, source: str) -> None:
        log.info(f'Start checking source: {source}')
        log.info(f'Source code is:\n{get_content_from_file(source)}')
        expected_out = self.__calculate_expression_safely(self.__get_python_popen_args(source))
        actual_out = self.__get_actual_out(source)
        log.info(f'Expected out is: {expected_out}. Actual out is: {actual_out}')
        assert expected_out == actual_out
