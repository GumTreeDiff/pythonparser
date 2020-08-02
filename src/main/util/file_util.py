# Copyright (c) Aniskov N., Birillo A.

import os
from typing import Callable, List

from src.main.util.const import FILE_SYSTEM_ITEM, ISO_ENCODING

ItemCondition = Callable[[str], bool]


def all_items_condition(name: str) -> bool:
    return True


def is_init_file(name: str) -> bool:
    return '__init__.py' in name


# To get all files or subdirs (depends on the last parameter) from root that match item_condition
# Note that all subdirs or files already contain the full path for them
def get_all_file_system_items(root: str, item_condition: ItemCondition = all_items_condition,
                              item_type: FILE_SYSTEM_ITEM = FILE_SYSTEM_ITEM.FILE,
                              to_ignore_init_files: bool = True) -> List[str]:
    items = []
    for fs_tuple in os.walk(root):
        for item in fs_tuple[item_type.value]:
            if to_ignore_init_files and is_init_file(item):
                continue
            if item_condition(item):
                items.append(os.path.join(fs_tuple[FILE_SYSTEM_ITEM.PATH.value], item))
    return items


def create_directory(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)


# File should contain the full path and its extension
def create_file(content: str, file: str) -> None:
    create_directory(os.path.dirname(file))
    with open(file, 'w') as f:
        f.write(content)


def is_file(file: str) -> bool:
    return os.path.isfile(file)


def remove_file(file: str) -> None:
    if is_file(file):
        os.remove(file)


def get_content_from_file(file: str, encoding: str = ISO_ENCODING, to_strip_nl: bool = True) -> str:
    with open(file, 'r', encoding=encoding) as f:
        content = f.read()
        return content if not to_strip_nl else content.rstrip('\n')
