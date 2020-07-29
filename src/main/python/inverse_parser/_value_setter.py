# Copyright (c) Aniskov N.
from typing import *
from pydoc import locate
import ast
import xml.etree.ElementTree as ET
from src.main.util.const import DEFAULT_ENCODING


class _ValueSetter:

    @staticmethod
    def set_value(xml_node: ET.Element, py_node: ast.AST, py_node_attrib_name: str) -> None:
        """
        :param xml_node:
        :param py_node:
        :param py_node_attrib_name:
        """
        if 'value_type' not in xml_node.attrib:
            raise RuntimeError(f'missing value_type attribute in {xml_node.tag} node')

        str_val_repr = xml_node.attrib['value']
        str_val_type_repr = xml_node.attrib['value_type']

        value_type = locate(str_val_type_repr)

        if str_val_type_repr == 'ellipsis':
            value = ...
        elif not value_type:
            raise RuntimeError(f'failed to locate Constant.value type: {xml_node.attrib["value_type"]}')

        elif value_type == bytes:
            value = value_type(str_val_repr[2:len(str_val_repr) - 1].encode(DEFAULT_ENCODING))
        else:
            value = value_type(str_val_repr)

        setattr(py_node, py_node_attrib_name, value)



