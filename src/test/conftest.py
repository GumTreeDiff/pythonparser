# Copyright (c) Aniskov N., Birillo A.

# Set file for logger before all tests
from src.main.util.log_util import configure_logger


def pytest_configure(config):
    configure_logger(in_test_mode=True, to_delete_previous_logs=True)
