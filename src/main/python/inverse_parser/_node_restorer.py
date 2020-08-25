# Copyright (c) Aniskov N.

import ast
import logging
import xml.etree.ElementTree as ET
from typing import *

from src.main.python.inverse_parser._attribute_setter import _AttributeSetter
from src.main.python.inverse_parser._merged_types_restorer import _MergedTypesRestorer
from src.main.python.inverse_parser._xml_node_children_getter import _XmlNodeChildrenGetter
from src.main.util.const import LOGGER_NAME
from src.main.util.log_util import log_and_raise_error

logger = logging.getLogger(LOGGER_NAME)


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
        if not py_node_type == ast.Module and not py_node_type == type(None):  # ast.Module doesn't need to be localized
            _NodeRestorer.localize_node(xml_node, py_node)

        try:
            restore_py_node = _NodeRestorer.py_node_type_to_restorer[py_node_type]

        except KeyError:
            log_and_raise_error(f'Unknown node type: {py_node_type}.',
                                logger,
                                RuntimeError)

        restore_py_node(xml_node, py_node)
        return py_node

    # Node restorers:

    # - Literals:

    @staticmethod
    def restore_ast_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='value')

    @staticmethod
    def restore_ast_num(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='n')

    @staticmethod
    def restore_ast_str(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.s = xml_node.attrib['value']

    @staticmethod
    def restore_ast_bytes(xml_node: ET.Element, py_node: ast.AST) -> None:  # Deprecated in Python 3.8 +
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='s')

    @staticmethod
    def restore_ast_formatted_value(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_children[0])
        py_node.conversion = -1
        try:
            py_node.format_spec = _NodeRestorer.restore(xml_node_children[1])
        except IndexError:
            py_node.format_spec = None
        ''' 
        Note: conversion=-1 is "no formatting". So it'll be default setting.
        It is possible to include conversion in XML if neccessary
        '''
    @staticmethod
    def restore_joined_str(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.values = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_list(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_tuple(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_set(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elts = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_dict(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        num_children = len(xml_node_children)
        assert len(xml_node_children) % 2 == 0, 'expected that (number of keys) == (number of values) in dict'
        py_node.keys = _NodeRestorer.restore_many(xml_node_children[:num_children // 2])
        py_node.values = _NodeRestorer.restore_many(xml_node_children[num_children // 2:])

    @staticmethod
    def restore_ast_ellipsis(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='value')

    @staticmethod
    def restore_ast_name_constant(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='value')

    # - Variables:

    @staticmethod
    def restore_ast_name(xml_node: ET.Element, py_node: ast.AST):
        py_node.id = xml_node.attrib['value']

    # Load, Store, Del are accounted for in set_ctx_and_ops method
    @staticmethod
    def restore_ast_starred(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_child = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_child)

    # - Expressions:

    @staticmethod
    def restore_ast_expr(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_child = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_child)

    @staticmethod
    def restore_ast_unary_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_operand = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.operand = _NodeRestorer.restore(xml_operand)

    # UAdd, USub, Not, Invert are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_bin_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        left_xml_operand, right_xml_operand = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.left = _NodeRestorer.restore(left_xml_operand)
        py_node.right = _NodeRestorer.restore(right_xml_operand)

    # Add, Sub, Mult, .. etc are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_bool_op(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.values = _NodeRestorer.restore_many(xml_node_children)

    # And, Or are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_compare(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)

        py_node.left = _NodeRestorer.restore(xml_node_children[0])
        py_node.comparators = _NodeRestorer.restore_many(xml_node_children[1:])

    # Eq. NotEq, Lt, .. etc are accounted for in set_ctx_and_ops method

    @staticmethod
    def restore_ast_call(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)

        try:
            args_kwargs_idx_delimiter = next(filter(
                lambda enumerated_node: enumerated_node[1].tag.startswith('keyword'),
                enumerate(xml_node_children)))[0]
        except StopIteration:
            args_kwargs_idx_delimiter = len(xml_node_children)

        py_node.func = _NodeRestorer.restore(xml_node_children[0])
        py_node.args = _NodeRestorer.restore_many(xml_node_children[1:args_kwargs_idx_delimiter])
        py_node.keywords = _NodeRestorer.restore_many(xml_node_children[args_kwargs_idx_delimiter:])

    @staticmethod
    def restore_ast_keyword(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_const_attrib(xml_node, py_node, py_node_attrib_name='arg')
        py_node.value = _NodeRestorer.restore(_XmlNodeChildrenGetter.get_unique_child(xml_node))

    @staticmethod
    def restore_ast_if_exp(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.test = _NodeRestorer.restore(xml_node_children[0])
        py_node.body = _NodeRestorer.restore(xml_node_children[1])
        py_node.orelse = _NodeRestorer.restore(xml_node_children[2])

    @staticmethod
    def restore_ast_attribute(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_children[0])
        py_node.attr = xml_node_children[1].attrib['value']

    # - Subscripting:

    @staticmethod
    def restore_ast_subscript(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_children[0])
        py_node.slice = _NodeRestorer.restore(xml_node_children[1])

    @staticmethod
    def restore_ast_index(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_child = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_child)

    @staticmethod
    def restore_ast_slice(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_lower = _XmlNodeChildrenGetter.get_unique_child(xml_node, 'lower')
        xml_node_step = _XmlNodeChildrenGetter.get_unique_child(xml_node, 'step')
        xml_node_upper = _XmlNodeChildrenGetter.get_unique_child(xml_node, 'upper')

        xml_node_lower_val = _XmlNodeChildrenGetter.get_unique_child(xml_node_lower)
        xml_node_step_val = _XmlNodeChildrenGetter.get_unique_child(xml_node_step)
        xml_node_upper_val = _XmlNodeChildrenGetter.get_unique_child(xml_node_upper)

        if xml_node_lower_val is not None:
            py_node.lower = _NodeRestorer.restore(xml_node_lower_val)
        else:
            py_node.lower = None

        if xml_node_step_val is not None:
            py_node.step = _NodeRestorer.restore(xml_node_step_val)
        else:
            py_node.step = None

        if xml_node_upper_val is not None:
            py_node.upper = _NodeRestorer.restore(xml_node_upper_val)
        else:
            py_node.upper = None


    @staticmethod
    def restore_ast_ext_slice(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.dims = _NodeRestorer.restore_many(xml_node_children)

    # - Comprehensions:

    @staticmethod
    def restore_ast_list_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elt = _NodeRestorer.restore(xml_node_children[0])
        xml_node_children_comps = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='comprehension')
        py_node.generators = _NodeRestorer.restore_many(xml_node_children_comps)

    @staticmethod
    def restore_ast_set_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elt = _NodeRestorer.restore(xml_node_children[0])
        xml_node_children_comps = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='comprehension')
        py_node.generators = _NodeRestorer.restore_many(xml_node_children_comps)

    @staticmethod
    def restore_ast_generator_exp(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.elt = _NodeRestorer.restore(xml_node_children[0])
        xml_node_children_comps = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='comprehension')
        py_node.generators = _NodeRestorer.restore_many(xml_node_children_comps)

    @staticmethod
    def restore_ast_dict_comp(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.key = _NodeRestorer.restore(xml_node_children[0])
        py_node.value = _NodeRestorer.restore(xml_node_children[1])
        xml_node_children_comps = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='comprehension')
        py_node.generators = _NodeRestorer.restore_many(xml_node_children_comps)

    @staticmethod
    def restore_ast_comprehension(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.iter = _NodeRestorer.restore(xml_node_children[1])
        py_node.ifs = _NodeRestorer.restore_many(xml_node_children[2:])
        #  py_node.is_async = ? TODO: parser doesn't account async's

    # - Statements:

    @staticmethod
    def restore_ast_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node_children = _NodeRestorer.restore_many(xml_node_children)
        py_node.targets = py_node_children[:-1]
        py_node.value = py_node_children[-1]

    @staticmethod
    def restore_ast_ann_assign(xml_node: ET.Element, py_node: ast.AST) -> None:  # TODO: astmonkey.to_source doesn’t support AnnAssign
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.annotation = _NodeRestorer.restore(xml_node_children[1])
        py_node.value = _NodeRestorer.restore(xml_node_children[2])
        #  py_node.simple = ? TODO: parser doesn't account "simple" field

    @staticmethod
    def restore_ast_aug_assign(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.value = _NodeRestorer.restore(xml_node_children[1])

    @staticmethod
    def restore_ast_raise(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.exc = _NodeRestorer.restore(xml_node_children[0])
        try:
            py_node.cause = _NodeRestorer.restore(xml_node_children[1])
        except IndexError:
            py_node.cause = None

    @staticmethod
    def restore_ast_assert(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.test = _NodeRestorer.restore(xml_node_children[0])
        try:
            py_node.msg = _NodeRestorer.restore(xml_node_children[1])
        except IndexError:
            py_node.msg = None

    @staticmethod
    def restore_ast_delete(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.targets = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_pass(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # - Imports:

    @staticmethod
    def restore_ast_import(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.names = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_import_from(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.module = xml_node.attrib['value'] if 'value' in xml_node.attrib else None
        py_node.level = int(xml_node.tag.split('-')[1])
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.names = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_alias(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']
        xml_identifier = xml_node.find('identifier')
        py_node.asname = xml_identifier.attrib['value'] if xml_identifier is not None else None

    # - Control flow:

    @staticmethod
    def restore_ast_if(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.test = _NodeRestorer.restore(xml_node_children[0])

        xml_node_body = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='body')
        xml_node_body_children = _XmlNodeChildrenGetter.get_children(xml_node_body)
        py_node.body = _NodeRestorer.restore_many(xml_node_body_children)

        _AttributeSetter.set_list_field(xml_node, py_node, 'orelse')

    @staticmethod
    def restore_ast_for(xml_node: ET.Element, py_node: ast.AST) -> None:  # TODO: note in README that "type comment"s are not supported by parser
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.target = _NodeRestorer.restore(xml_node_children[0])
        py_node.iter = _NodeRestorer.restore(xml_node_children[1])

        xml_node_body = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='body')
        xml_node_body_children = _XmlNodeChildrenGetter.get_children(xml_node_body)
        py_node.body = _NodeRestorer.restore_many(xml_node_body_children)

        _AttributeSetter.set_list_field(xml_node, py_node, 'orelse')

    @staticmethod
    def restore_ast_while(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.test = _NodeRestorer.restore(xml_node_children[0])

        xml_node_body = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='body')
        xml_node_body_children = _XmlNodeChildrenGetter.get_children(xml_node_body)
        py_node.body = _NodeRestorer.restore_many(xml_node_body_children)

        _AttributeSetter.set_list_field(xml_node, py_node, 'orelse')

    @staticmethod
    def restore_ast_break(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_continue(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    @staticmethod
    def restore_ast_try(xml_node: ET.Element, py_node: ast.AST) -> None:

        xml_node_body = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='body')
        xml_node_body_children = _XmlNodeChildrenGetter.get_children(xml_node_body)
        py_node.body = _NodeRestorer.restore_many(xml_node_body_children)

        xml_node_handlers = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='handlers')
        xml_node_handlers_children = _XmlNodeChildrenGetter.get_children(xml_node_handlers)
        py_node.handlers = _NodeRestorer.restore_many(xml_node_handlers_children)

        _AttributeSetter.set_list_field(xml_node, py_node, 'orelse')
        _AttributeSetter.set_list_field(xml_node, py_node, 'finalbody')

    @staticmethod
    def restore_ast_except_handler(xml_node: ET.Element, py_node: ast.AST) -> None:
        try:
            py_node.name = xml_node.attrib['value']
        except KeyError:
            py_node.name = None

        xml_exc_type_node = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='type')
        if xml_exc_type_node is not None:
            py_node.type = _NodeRestorer.restore(_XmlNodeChildrenGetter.get_unique_child(xml_exc_type_node))

        else:
            py_node.type = None

        xml_exc_body_node = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='body')
        if xml_exc_body_node is not None:
            py_node.body = _NodeRestorer.restore_many(_XmlNodeChildrenGetter.get_children(xml_exc_body_node))
        else:
            py_node.body = None

    @staticmethod
    def restore_ast_with(xml_node: ET.Element, py_node: ast.AST) -> None:
        _AttributeSetter.set_list_field(xml_node, py_node, 'items')
        _AttributeSetter.set_list_field(xml_node, py_node, 'body')

        # py_node.typecomment = ? TODO: parser doesn't account "typecomment" field

    @staticmethod
    def restore_ast_withitem(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.context_expr = _NodeRestorer.restore(xml_node_children[0])

        try:
            py_node.optional_vars = _NodeRestorer.restore(xml_node_children[1])
        except IndexError:
            py_node.optional_vars = None

    # - Function and class definitions:

    @staticmethod
    def restore_ast_function_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

        xml_node_arguments = _XmlNodeChildrenGetter.get_unique_child(xml_node, 'arguments')
        py_node.args = _NodeRestorer.restore(xml_node_arguments)

        _AttributeSetter.set_list_field(xml_node, py_node, 'body')
        _AttributeSetter.set_list_field(xml_node, py_node, 'decorator_list')

    @staticmethod
    def restore_ast_lambda(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        xml_node_arguments = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='arguments')
        if xml_node_arguments is not None:
            py_node.args = _NodeRestorer.restore(xml_node_arguments)
        else:
            py_node.args = None

        try:
            xml_node_body = xml_node_children[1]
            py_node.body = _NodeRestorer.restore(xml_node_body)
        except IndexError:
            py_node.body = None

    @staticmethod
    def restore_ast_arguments(xml_node: ET.Element, py_node: ast.AST) -> None:

        _AttributeSetter.set_list_field(xml_node, py_node, 'posonlyargs')
        _AttributeSetter.set_list_field(xml_node, py_node, 'args')
        _AttributeSetter.set_list_field(xml_node, py_node, 'kwonlyargs')
        _AttributeSetter.set_list_field(xml_node, py_node, 'kw_defaults')
        _AttributeSetter.set_list_field(xml_node, py_node, 'defaults')

        xml_node_vararg = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='vararg')
        if xml_node_vararg is not None:
            py_node.vararg = ast.arg(arg=xml_node_vararg.attrib['value'], annotation=None)
        else:
            py_node.vararg = None

        xml_node_kwarg = _XmlNodeChildrenGetter.get_unique_child(xml_node, with_tag='kwarg')
        if xml_node_kwarg is not None:
            py_node.kwarg = ast.arg(arg=xml_node_kwarg.attrib['value'], annotation=None)
        else:
            py_node.kwarg = None

    @staticmethod
    def restore_ast_arg(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.arg = xml_node.attrib['value']
        py_node.annotation = None  # pythonparser_3 does not support type annotation

    @staticmethod
    def restore_ast_return(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_value = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        if xml_node_value is not None:
            py_node.value = _NodeRestorer.restore(xml_node_value)
        else:
            py_node.value = None

    @staticmethod
    def restore_ast_yield(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_value = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        if xml_node_value is not None:
            py_node.value = _NodeRestorer.restore(xml_node_value)
        else:
            py_node.value = None

    @staticmethod
    def restore_ast_yield_from(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_value = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        if xml_node_value is not None:
            py_node.value = _NodeRestorer.restore(xml_node_value)
        else:
            py_node.value = None

    @staticmethod
    def restore_ast_global(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='identifier')
        py_node.names = [elem.attrib['value']
                         for elem in xml_node_children]

    @staticmethod
    def restore_ast_nonlocal(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node, with_tag='identifier')
        py_node.names = [elem.attrib['value']
                         for elem in xml_node_children]

    @staticmethod
    def restore_ast_class_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        py_node.name = xml_node.attrib['value']

        _AttributeSetter.set_list_field(xml_node, py_node, 'bases')
        _AttributeSetter.set_list_field(xml_node, py_node, 'keywords')
        _AttributeSetter.set_list_field(xml_node, py_node, 'body')
        _AttributeSetter.set_list_field(xml_node, py_node, 'decorator_list')

    # - Async and await:

    @staticmethod
    def restore_ast_async_function_def(xml_node: ET.Element, py_node: ast.AST) -> None:
        _NodeRestorer.restore_ast_function_def(xml_node, py_node)

    @staticmethod
    def restore_ast_await(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_child = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.value = _NodeRestorer.restore(xml_node_child)

    @staticmethod
    def restore_ast_async_for(xml_node: ET.Element, py_node: ast.AST) -> None:
        _NodeRestorer.restore_ast_for(xml_node, py_node)

    @staticmethod
    def restore_ast_async_with(xml_node: ET.Element, py_node: ast.AST) -> None:
        _NodeRestorer.restore_ast_with(xml_node, py_node)

    # - Top level nodes:

    @staticmethod
    def restore_ast_module(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.body = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_interactive(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_children = _XmlNodeChildrenGetter.get_children(xml_node)
        py_node.body = _NodeRestorer.restore_many(xml_node_children)

    @staticmethod
    def restore_ast_expression(xml_node: ET.Element, py_node: ast.AST) -> None:
        xml_node_child = _XmlNodeChildrenGetter.get_unique_child(xml_node)
        py_node.body = _NodeRestorer.restore(xml_node_child)

    # - Corner cases:

    @staticmethod
    def restore_nonetype(xml_node: ET.Element, py_node: ast.AST) -> None:
        pass

    # Helper methods:

    @staticmethod
    def localize_node(xml_node: ET.Element, py_node: ast.AST) -> None:
        try:
            py_node.col_offset = int(xml_node.attrib['col'])
            py_node.end_col_offset = int(xml_node.attrib['end_col'])
            py_node.lineno = int(xml_node.attrib['lineno'])
            py_node.end_lineno = int(xml_node.attrib['end_line_no'])
        except KeyError:
            pass  # code generation can work without information about the positions of the tokens

    @staticmethod
    def restore_many(xml_node_list: List[ET.Element]) -> List[ast.AST]:
        result = [_NodeRestorer.restore(xml_node) for xml_node in xml_node_list]
        return result


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
    ast.Expression:  _NodeRestorer.restore_ast_expression,

    # - Corner cases:
    type(None): _NodeRestorer.restore_nonetype

    # No default handler
}


