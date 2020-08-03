# Copyright (c) Aniskov N.
import ast
import xml.etree.ElementTree as ET
from pydoc import locate

import src.main.python.inverse_parser._node_restorer as nr
from src.main.python.inverse_parser._xml_node_children_getter import _XmlNodeChildrenGetter
from src.main.util.const import DEFAULT_ENCODING


class _AttributeSetter:

    @staticmethod
    def set_const_value(xml_node: ET.Element, py_node: ast.AST, py_node_attrib_name: str) -> None:
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
        elif str_val_type_repr == 'NoneType':
            value = None
        elif not value_type:
            raise RuntimeError(f'failed to locate Constant.value type: {xml_node.attrib["value_type"]}')

        elif value_type == bytes:
            value = value_type(str_val_repr[2:len(str_val_repr) - 1].encode(DEFAULT_ENCODING))

        elif value_type == bool:
            value = str_val_repr == 'True'

        else:
            value = value_type(str_val_repr)

        setattr(py_node, py_node_attrib_name, value)

    @staticmethod
    def set_list_field(xml_node: ET.Element, py_node: ast.AST, py_node_field_name: str) -> None:
        xml_node_of_field = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag=py_node_field_name)
        if xml_node_of_field is not None:
            xml_node_of_field_children = _XmlNodeChildrenGetter.get_children(xml_node_of_field)
            setattr(py_node, py_node_field_name, nr._NodeRestorer.restore_many(xml_node_of_field_children))
        else:
            setattr(py_node, py_node_field_name, [])





