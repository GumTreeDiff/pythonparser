# Copyright (c) Aniskov N.

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
TEST_RESOURCES_PATH = os.path.join(ROOT_DIR, 'src/test/resources')

DEFAULT_ENCODING = 'utf-8'
