# Copyright (c) Aniskov N., Birillo A.

import os
import logging
from typing import List, Tuple

import pytest

from src.test.python.inverse_parser.util import InverseParserTestsUtil
from src.main.util.const import TEST_RESOURCES_PATH, LOGGER_NAME, FILE_SYSTEM_ITEM
from src.main.util.file_util import get_all_file_system_items, match_condition, pair_in_and_out_files

log = logging.getLogger(LOGGER_NAME)


INPUT_DIR = os.path.join(TEST_RESOURCES_PATH, 'inverse_parser/inverse_parser_3')
ALL_TEST_DIR = get_all_file_system_items(INPUT_DIR, lambda x: 'case' in x, FILE_SYSTEM_ITEM.SUBDIR)


class TestInverseParser3:

    # The function returns list of tests pairs. For example: [(in_1, out_1), (in_2, out_2)]
    @staticmethod
    def __get_test_in_and_out_files(root: str) -> List[Tuple[str, str]]:
        in_files = get_all_file_system_items(root, match_condition(r'in_\d+.py'))
        out_files = get_all_file_system_items(root, match_condition(r'out_\d+.py'))
        assert len(in_files) != 0, f'Number of test files is zero! Root for files is {root}'
        return pair_in_and_out_files(in_files, out_files)

    @pytest.mark.parametrize('case_dir', ALL_TEST_DIR)
    def test_generated_code_is_eq_to_original(self, case_dir: str, subtests) -> None:
        log.info(f'Start testing {case_dir} folder')
        in_and_out_files = self.__get_test_in_and_out_files(case_dir)
        log.info(f'Have collected {len(in_and_out_files)} pairs for tests')

        for in_file, out_file in in_and_out_files:
            log.info(f'Current in file is {in_file}, current out file us: {out_file}')

            with subtests.test(in_file=in_file, out_file=out_file):
                actual_out = InverseParserTestsUtil.source_to_xml_to_source(in_file)
                expected_out = InverseParserTestsUtil.get_source_from_file(out_file)
                log.info(f'Expected out is:\n{expected_out}\nActual out is:\n{actual_out}')
                assert actual_out == expected_out
