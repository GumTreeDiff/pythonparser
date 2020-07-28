# Copyright (c) Aniskov N.

import ast
import xml.etree.ElementTree as ET

from astmonkey import visitors

from src.main.python.inverse_parser._node_restorer import _NodeRestorer


class InverseParser:
    """
    Class converts AST in XML format to Python AST object
    """
    def __init__(self, filename: str = None, xml_str: str = None):
        """
        constructor requires one of the following parameters, but not both at the same time:
        :param filename: path to file containing AST in XML format
        :param xml_str: string, containing AST in XML format
        """
        if not filename and not xml_str:
            raise ValueError('Either "filename" or "xml_str" must not be None.')

        if filename and xml_str:
            raise ValueError('Only one of the "filename" and "xml_str" must be provided. Not both.')

        if filename:
            self.__init_xml_ast(filename)
        else:
            self.xml_ast_ = ET.fromstring(xml_str)

        self.py_ast_ = None

    def get_source(self) -> str:
        """
        :return: Python 3 source code
        """
        py_ast = self.get_py_ast()
        generated_src = visitors.to_source(py_ast)
        return generated_src

    def get_py_ast(self) -> ast.AST:
        """
        Converts AST in XML format to Python AST object
        :return: Python AST root
        """
        if self.py_ast_:
            return self.py_ast_

        py_ast = _NodeRestorer.restore(self.xml_ast_)
        return py_ast

    def get_xml_ast(self) -> ET.Element:
        return self.xml_ast_

    def __init_xml_ast(self, filename: str) -> None:
        with open(filename, 'rt') as f:
            xml_str = f.read()
            self.xml_ast_ = ET.fromstring(xml_str)
