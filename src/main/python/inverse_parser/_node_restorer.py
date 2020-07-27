# Copyright (c) Aniskov N.

import ast
import xml.etree.ElementTree as ET
from typing import *
import warnings

from src.main.python.inverse_parser._merged_types_restorer import _MergedTypesRestorer


class _NodeRestorer:

    @staticmethod
    def restore(xml_node: ET.Element) -> ast.AST:
        """
        Partially restores python AST from XML AST recursively
        :param xml_node: AST node in xml format to restore
        :return: partially restored python AST
        """

        (py_node_type, merged_types) = _MergedTypesRestorer.get_types_from_tag(xml_node)
        py_node = py_node_type()
        _MergedTypesRestorer.set_ctx_and_ops(py_node, merged_types)
        if not py_node_type == ast.Module:  # ast.Module doesn't need to be localized
            _NodeRestorer.localize_node(xml_node, py_node)

        try:
            restore_py_node = _NodeRestorer.py_node_type_to_restorer[py_node_type]

        except KeyError:
            restore_py_node = _NodeRestorer.py_node_type_to_restorer['default']
            warnings.warn(f'Restorer for {py_node_type} is unsupported yet. Default restorer will be called')

        restore_py_node(xml_node, py_node)
        return py_node

    # Node restorers:

    @staticmethod
    def restore_name(xml_node: ET.Element, py_node: ast.AST):
        py_node.id = xml_node.attrib['value']

    @staticmethod
    def restore_name_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.value = xml_node.attrib['value']

    @staticmethod
    def restore_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        str_val_repr = xml_node.attrib['value']
        py_node.value = _NodeRestorer.try_get_numeric_value(str_val_repr)

    @staticmethod
    def restore_num(xml_node: ET.Element, py_node: ast.AST) -> None:
        str_val_repr = xml_node.attrib['value']
        py_node.n = _NodeRestorer.try_get_numeric_value(str_val_repr)

    @staticmethod
    def restore_str(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.s = xml_node.attrib['value']

    @staticmethod
    def restore_alias(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']
        xml_identifier = xml_node.find('identifier')
        py_node.asname = xml_identifier.attrib['value'] if xml_identifier is not None else None

    @staticmethod
    def restore_function_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

    @staticmethod
    def restore_except_handler(xml_node: ET.Element, py_node: ast.AST) -> None:
        if 'value' in xml_node.attrib:
            py_node.name = xml_node.attrib['value']

    @staticmethod
    def restore_class_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

    @staticmethod
    def restore_import(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.names = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_import_from(xml_node: ET.Element, py_node: ast.AST) -> None:
        if 'value' in xml_node.attrib:
            py_node.module = xml_node.attrib['value']

    @staticmethod
    def restore_global(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.names = [elem.attrib['value']
                         for elem in xml_node.findall('identifier')]

    @staticmethod
    def restore_keyword(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.arg = xml_node.attrib['value']

    @staticmethod
    def restore_arg(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.arg = xml_node.attrib['value']

    @staticmethod
    def restore_tuple(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_list(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node_children = _NodeRestorer.restore_many(xml_node_children)
        py_node.targets = py_node_children[:-1]
        py_node.value = py_node_children[-1]

    @staticmethod
    def restore_for(xml_node: ET.Element, py_node: ast.AST) -> None:  # TODO: note in README that "type comment"s are not supported by parser
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.iter = _NodeRestorer.restore(xml_node_children[1])
        # assert xml_node_children[2].tag == 'body'  # should be body in XML_For layout
        py_node.body = [_NodeRestorer.restore(xml_body_item)
                        for xml_body_item in xml_node_children[2]]
        xml_orelse_children = _NodeRestorer.get_xml_node_children(xml_node_children[3])
        py_node.orelse = _NodeRestorer.restore_many(xml_orelse_children)

    @staticmethod
    def restore_bin_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.left = _NodeRestorer.restore(xml_node_children[0])
        py_node.right = _NodeRestorer.restore(xml_node_children[1])

    @staticmethod
    def restore_bool_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.values = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_unary_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_operand = _NodeRestorer.get_xml_node_children(xml_node)[0]
        py_node.operand = _NodeRestorer.restore(xml_operand)

    @staticmethod
    def restore_module(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        if xml_node_children and ('body' in py_node._fields) and not hasattr(py_node, 'body'):
            py_node.body = [_NodeRestorer.restore(xml_node_child) for xml_node_child in xml_node_children]

    # TODO: write better default handler
    @staticmethod
    def restore_default(xml_node: ET.Element, py_node: ast.AST) -> None:
        _NodeRestorer.restore_module(xml_node, py_node) # the same as restore module at that point

    # Helper methods:

    @staticmethod
    def localize_node(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.col_offset = int(xml_node.attrib['col'])
        py_node.end_col_offset = int(xml_node.attrib['end_col'])
        py_node.lineno = int(xml_node.attrib['lineno'])
        py_node.end_lineno = int(xml_node.attrib['end_lineno'])

    @staticmethod
    def restore_many(xml_node_list: List[ET.Element]) -> List[ast.AST]:
        result = [_NodeRestorer.restore(xml_node) for xml_node in xml_node_list]
        return result

    @staticmethod
    def get_xml_node_children(xml_node):
        return [child for child in xml_node]

    @staticmethod
    def try_get_numeric_value(str_val_repr):  # TODO: if this is not enough, then it is necessary to insert type of Constant explicitly to XML
        val = str_val_repr
        try:
            val = int(str_val_repr)
        except ValueError:
            try:
                val = float(str_val_repr)
            except ValueError:
                pass
        return val


_NodeRestorer.py_node_type_to_restorer = {
    ast.Module: _NodeRestorer.restore_module,
    ast.Name: _NodeRestorer.restore_name,
    ast.Constant: _NodeRestorer.restore_constant,
    ast.NameConstant: _NodeRestorer.restore_name_constant,
    ast.Num: _NodeRestorer.restore_num,
    ast.Str: _NodeRestorer.restore_str,
    ast.alias: _NodeRestorer.restore_alias,
    ast.FunctionDef: _NodeRestorer.restore_function_def,
    ast.ExceptHandler: _NodeRestorer.restore_except_handler,
    ast.ClassDef: _NodeRestorer.restore_class_def,
    ast.Import: _NodeRestorer.restore_import,
    ast.ImportFrom: _NodeRestorer.restore_import_from,
    ast.Global: _NodeRestorer.restore_global,
    ast.keyword: _NodeRestorer.restore_keyword,
    ast.arg: _NodeRestorer.restore_arg,
    ast.Tuple: _NodeRestorer.restore_tuple,
    ast.List: _NodeRestorer.restore_list,
    ast.Assign: _NodeRestorer.restore_assign,
    ast.BinOp: _NodeRestorer.restore_bin_op,
    ast.BoolOp: _NodeRestorer.restore_bool_op,
    ast.UnaryOp: _NodeRestorer.restore_unary_op,
    ast.For: _NodeRestorer.restore_for,
    'default': _NodeRestorer.restore_default
}



