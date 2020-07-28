# Copyright (c) Aniskov N.

import ast
import xml.etree.ElementTree as ET
from typing import *

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
            raise NotImplementedError(f'Restorer for {py_node_type} is unsupported yet')

        restore_py_node(xml_node, py_node)
        return py_node

    # Node restorers:

    # - Literals:

    @staticmethod
    def restore_ast_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        str_val_repr = xml_node.attrib['value']
        py_node.value = _NodeRestorer.try_get_numeric_value(str_val_repr)

    @staticmethod
    def restore_ast_num(xml_node: ET.Element, py_node: ast.AST) -> None:
        str_val_repr = xml_node.attrib['value']
        py_node.n = _NodeRestorer.try_get_numeric_value(str_val_repr)

    @staticmethod
    def restore_ast_str(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.s = xml_node.attrib['value']

    @staticmethod
    def restore_ast_bytes(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_formatted_value(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_joined_str(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_list(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_tuple(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_set(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_dict(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        num_children = len(xml_node_children)
        assert len(xml_node_children) % 2 == 0, 'expected that (number of keys) == (number of values) in dict'
        py_node.keys = _NodeRestorer.restore_many(xml_node_children[:num_children // 2])
        py_node.values = _NodeRestorer.restore_many(xml_node_children[num_children // 2:])

    @staticmethod
    def restore_ast_ellipsis(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_name_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.value = xml_node.attrib['value']

    # - Variables:

    @staticmethod
    def restore_ast_name(xml_node: ET.Element, py_node: ast.AST):
        py_node.id = xml_node.attrib['value']

    # Load, Store, Del are accounted for in set_ctx_and_ops method
    @staticmethod
    def restore_ast_starred(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_children[0])

    # - Expressions:

    @staticmethod
    def restore_ast_expr(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_children[0])

    @staticmethod
    def restore_ast_unary_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_operand = _NodeRestorer.get_xml_node_children(xml_node)[0]
        py_node.operand = _NodeRestorer.restore(xml_operand)

    # UAdd, USub, Not, Invert are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_bin_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.left = _NodeRestorer.restore(xml_node_children[0])
        py_node.right = _NodeRestorer.restore(xml_node_children[1])

    # Add, Sub, Mult, .. etc are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_bool_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.values = _NodeRestorer.restore_many(xml_node_children)

    # And, Or are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_compare(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)

        py_node.left = _NodeRestorer.restore(xml_node_children[0])
        py_node.comparators = _NodeRestorer.restore_many(xml_node_children[1:])

    # Eq. NotEq, Lt, .. etc are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_call(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)

        args_kwargs_idx_delimiter = next(filter(
            lambda enumerated_node: enumerated_node[1].tag == 'keyword',
            enumerate(xml_node_children)))[0]

        py_node.func = _NodeRestorer.restore(xml_node_children[0])
        py_node.args = _NodeRestorer.restore_many(xml_node_children[1:args_kwargs_idx_delimiter])
        py_node.keywords = _NodeRestorer.restore_many(xml_node_children[args_kwargs_idx_delimiter:])

    @staticmethod
    def restore_ast_keyword(xml_node: ET.Element, py_node: ast.AST) -> None:
        if xml_node.attrib['value'] != 'None':
            py_node.arg = xml_node.attrib['value']
        else:
            py_node.arg = None
        py_node.value = _NodeRestorer.restore(_NodeRestorer.get_xml_node_children(xml_node)[0])

    @staticmethod
    def restore_ast_if_exp(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_attribute(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Subscripting:

    @staticmethod
    def restore_ast_subscript(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_index(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_slice(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_ext_slice(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Comprehensions:

    @staticmethod
    def restore_ast_list_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_set_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_generator_exp(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_dict_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_comprehension(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Statements:

    @staticmethod
    def restore_ast_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node_children = _NodeRestorer.restore_many(xml_node_children)
        py_node.targets = py_node_children[:-1]
        py_node.value = py_node_children[-1]

    @staticmethod
    def restore_ast_ann_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_aug_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_raise(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_assert(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_delete(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_pass(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Imports:

    @staticmethod
    def restore_ast_import(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.names = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_import_from(xml_node: ET.Element, py_node: ast.AST) -> None:
        if 'value' in xml_node.attrib:
            py_node.module = xml_node.attrib['value']

    @staticmethod
    def restore_ast_alias(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']
        xml_identifier = xml_node.find('identifier')
        py_node.asname = xml_identifier.attrib['value'] if xml_identifier is not None else None

    # - Control flow:

    @staticmethod
    def restore_ast_if(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)

        py_node.test = _NodeRestorer.restore(xml_node_children[0])

        # assert xml_node_children[1].tag == 'body'  # should be body in XML "If" layout
        xml_body_children = _NodeRestorer.get_xml_node_children(xml_node_children[1])
        py_node.body = _NodeRestorer.restore_many(xml_body_children)

        # assert xml_node_children[2].tag == 'orelse'  # should be orelse in XML "If" layout
        xml_orelse_children = _NodeRestorer.get_xml_node_children(xml_node_children[2])
        py_node.orelse = _NodeRestorer.restore_many(xml_orelse_children)

    @staticmethod
    def restore_ast_for(xml_node: ET.Element, py_node: ast.AST) -> None:  # TODO: note in README that "type comment"s are not supported by parser
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.iter = _NodeRestorer.restore(xml_node_children[1])
        # assert xml_node_children[2].tag == 'body'  # should be body in XML_For layout
        py_node.body = [_NodeRestorer.restore(xml_body_item)
                        for xml_body_item in xml_node_children[2]]
        xml_orelse_children = _NodeRestorer.get_xml_node_children(xml_node_children[3])
        py_node.orelse = _NodeRestorer.restore_many(xml_orelse_children)

    @staticmethod
    def restore_ast_while(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_break(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_continue(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_try(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # @staticmethod
    # def restore_ast_try_finally(xml_node: ET.Element, py_node: ast.AST) -> None:
    #     pass
    #
    # @staticmethod
    # def restore_ast_try_except(xml_node: ET.Element, py_node: ast.AST) -> None:
    #     pass

    @staticmethod
    def restore_ast_except_handler(xml_node: ET.Element, py_node: ast.AST) -> None:
        if 'value' in xml_node.attrib:
            py_node.name = xml_node.attrib['value']

    @staticmethod
    def restore_ast_with(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_withitem(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Function and class definitions:

    @staticmethod
    def restore_ast_function_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

    @staticmethod
    def restore_ast_lambda(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_arguments(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_arg(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.arg = xml_node.attrib['value']

    @staticmethod
    def restore_ast_return(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_yield(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_yield_from(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_global(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.names = [elem.attrib['value']
                         for elem in xml_node.findall('identifier')]

    @staticmethod
    def restore_ast_nonlocal(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_class_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

    # - Async and await:

    @staticmethod
    def restore_ast_async_function_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_await(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_async_for(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_async_with(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Top level nodes:

    @staticmethod
    def restore_ast_module(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _NodeRestorer.get_xml_node_children(xml_node)
        if xml_node_children and ('body' in py_node._fields) and not hasattr(py_node, 'body'):
            py_node.body = [_NodeRestorer.restore(xml_node_child) for xml_node_child in xml_node_children]

    @staticmethod
    def restore_ast_interactive(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_expression(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # No default handler.

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
    def get_xml_node_children(xml_node, with_tag=None):
        if with_tag:
            return xml_node.findall(with_tag)
        return xml_node.findall('*')

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
    # - Literals:
    ast.Constant: _NodeRestorer.restore_ast_constant,
    ast.Num: _NodeRestorer.restore_ast_num,
    ast.Str: _NodeRestorer.restore_ast_str,
    ast.Bytes: _NodeRestorer.restore_ast_bytes,
    ast.FormattedValue: _NodeRestorer.restore_ast_formatted_value,
    ast.JoinedStr: _NodeRestorer.restore_joined_str,
    ast.List: _NodeRestorer.restore_ast_list,
    ast.Tuple: _NodeRestorer.restore_ast_tuple,
    ast.Set: _NodeRestorer.restore_ast_set,
    ast.Dict: _NodeRestorer.restore_ast_dict,
    ast.Ellipsis: _NodeRestorer.restore_ast_ellipsis,
    ast.NameConstant: _NodeRestorer.restore_ast_name_constant,

    # - Variables:
    ast.Name: _NodeRestorer.restore_ast_name,
    ast.Starred: _NodeRestorer.restore_ast_starred,

    # - Expressions:
    ast.Expr: _NodeRestorer.restore_ast_expr,
    ast.UnaryOp: _NodeRestorer.restore_ast_unary_op,
    ast.BinOp: _NodeRestorer.restore_ast_bin_op,
    ast.BoolOp: _NodeRestorer.restore_ast_bool_op,
    ast.Compare: _NodeRestorer.restore_ast_compare,
    ast.Call: _NodeRestorer.restore_ast_call,
    ast.keyword: _NodeRestorer.restore_ast_keyword,
    ast.IfExp: _NodeRestorer.restore_ast_if_exp,
    ast.Attribute: _NodeRestorer.restore_ast_attribute,

    # - Subscripting:
    ast.Subscript: _NodeRestorer.restore_ast_subscript,
    ast.Index: _NodeRestorer.restore_ast_index,
    ast.Slice: _NodeRestorer.restore_ast_slice,
    ast.ExtSlice: _NodeRestorer.restore_ast_ext_slice,

    # - Comprehensions:
    ast.ListComp: _NodeRestorer.restore_ast_list_comp,
    ast.SetComp: _NodeRestorer.restore_ast_set_comp,
    ast.GeneratorExp: _NodeRestorer.restore_ast_generator_exp,
    ast.DictComp: _NodeRestorer.restore_ast_dict_comp,
    ast.comprehension: _NodeRestorer.restore_ast_comprehension,

    # - Statements:
    ast.Assign: _NodeRestorer.restore_ast_assign,
    ast.AnnAssign: _NodeRestorer.restore_ast_ann_assign,
    ast.AugAssign: _NodeRestorer.restore_ast_aug_assign,
    ast.Raise: _NodeRestorer.restore_ast_raise,
    ast.Assert: _NodeRestorer.restore_ast_assert,
    ast.Delete: _NodeRestorer.restore_ast_delete,
    ast.Pass: _NodeRestorer.restore_ast_pass,

    # - Imports:
    ast.Import: _NodeRestorer.restore_ast_import,
    ast.ImportFrom: _NodeRestorer.restore_ast_import_from,
    ast.alias: _NodeRestorer.restore_ast_alias,

    # - Control flow:
    ast.If: _NodeRestorer.restore_ast_if,
    ast.For: _NodeRestorer.restore_ast_for,
    ast.While: _NodeRestorer.restore_ast_while,
    ast.Break: _NodeRestorer.restore_ast_break,
    ast.Continue: _NodeRestorer.restore_ast_continue,
    ast.Try: _NodeRestorer.restore_ast_try,
    ast.ExceptHandler: _NodeRestorer.restore_ast_except_handler,
    ast.With: _NodeRestorer.restore_ast_with,
    ast.withitem: _NodeRestorer.restore_ast_withitem,

    # - Function and class definitions:
    ast.FunctionDef: _NodeRestorer.restore_ast_function_def,
    ast.Lambda: _NodeRestorer.restore_ast_lambda,
    ast.arguments: _NodeRestorer.restore_ast_arguments,
    ast.arg: _NodeRestorer.restore_ast_arg,
    ast.Return: _NodeRestorer.restore_ast_return,
    ast.Yield: _NodeRestorer.restore_ast_yield,
    ast.YieldFrom: _NodeRestorer.restore_ast_yield_from,
    ast.Global: _NodeRestorer.restore_ast_global,
    ast.Nonlocal: _NodeRestorer.restore_ast_nonlocal,
    ast.ClassDef: _NodeRestorer.restore_ast_class_def,

    # - Async and await:
    ast.AsyncFunctionDef: _NodeRestorer.restore_ast_async_function_def,
    ast.Await: _NodeRestorer.restore_ast_await,
    ast.AsyncFor: _NodeRestorer.restore_ast_async_for,
    ast.AsyncWith: _NodeRestorer.restore_ast_async_with,

    # - Top level nodes:
    ast.Module: _NodeRestorer.restore_ast_module,
    ast.Interactive: _NodeRestorer.restore_ast_interactive,
    ast.Expression:  _NodeRestorer.restore_ast_expression

    # No default handler
}


