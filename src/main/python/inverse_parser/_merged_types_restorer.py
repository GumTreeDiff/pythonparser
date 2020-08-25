# Copyright (c) Aniskov N.

import ast
import logging
import xml.etree.ElementTree as ET
from typing import Tuple, Union, Any, List

from src.main.util.const import LOGGER_NAME
from src.main.util.log_util import log_and_raise_error

logger = logging.getLogger(LOGGER_NAME)

_py_node_type_name_to_ast_type = \
    dict([(name, cls) for name, cls in ast.__dict__.items() if isinstance(cls, type)])


class _MergedTypesRestorer:
    """
    Class provides functionality to restore context and operations,
    encoded in XML nodes tags
    """

    @staticmethod
    def get_types_from_tag(xml_node: ET.Element) -> Tuple[Union[type, Any], List[type]]:
        """
        :param xml_node: node of AST in XML format
        :return py_node_type: type of corresponding Python AST node
        :return merged_types: other types merged in tag: context or operators
        """
        types = xml_node.tag.split('_')
        py_node_type_name, merged_types_names = types[0].split('-')[0], types[1:]
        if py_node_type_name == 'NoneType':
            py_node_type = type(None)
        else:
            py_node_type = _py_node_type_name_to_ast_type[py_node_type_name]
        merged_types = [_py_node_type_name_to_ast_type[merged_type_name]
                        for merged_type_name in merged_types_names]
        return py_node_type, merged_types

    @staticmethod
    def set_ctx_and_ops(py_node: ast.AST, merged_types: List[type]) -> None:
        """
        :param py_node: Python ast tree node
        :param merged_types: type of operators or context extracted from XML tag
        """
        if not merged_types:
            return

        if 'ctx' in py_node._fields:
            py_node.ctx = merged_types[0]()

        elif 'op' in py_node._fields:
            py_node.op = merged_types[0]()

        elif 'ops' in py_node._fields:
            py_node.ops = [op_type() for op_type in merged_types]

        else:
            log_and_raise_error(f'Failed to restore context or operators',
                                logger,
                                RuntimeError)

