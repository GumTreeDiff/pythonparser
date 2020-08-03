# Copyright (c) Aniskov N., Birillo A.

import sys
import logging
from typing import Type
from logging import Logger

from src.main.util.const import LOGGER_TEST_FILE, LOGGER_FILE, LOGGER_FORMAT


def log_and_raise_error(msg: str, log: Logger, error: Type[Exception] = ValueError) -> None:
    log.error(msg)
    raise error(msg)


def configure_logger(in_test_mode: bool = False, to_delete_previous_logs: bool = False) -> None:
    filename = LOGGER_TEST_FILE if in_test_mode else LOGGER_FILE
    filemode = 'w' if to_delete_previous_logs else 'a'
    logging.basicConfig(filename=filename, format=LOGGER_FORMAT, level=logging.INFO, filemode=filemode)


def add_console_stream(log: Logger) -> None:
    log.addHandler(logging.StreamHandler(sys.stdout))
