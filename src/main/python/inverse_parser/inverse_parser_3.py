# Copyright (c) Aniskov N.

import ast
import xml.etree.ElementTree as ET

from astmonkey import visitors

from src.main.python.inverse_parser._node_restorer import _NodeRestorer


class InverseParser:
    """
    Class containing converts AST in XML format to Python AST object
    """
    def __init__(self, filename_or_str_repr: str, from_string: bool = False):
        """
        :param filename_or_str_repr: path to file containing AST in XML format
        """
        if not from_string:
            self.filename_ = filename_or_str_repr
            self.xml_ast_ = None
        else:
            self.filename_ = None
            self.xml_ast_ = ET.fromstring(filename_or_str_repr)
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

        if not self.xml_ast_:
            self.xml_ast_ = self.__read_xml_ast()

        py_ast = _NodeRestorer.restore(self.xml_ast_)
        return py_ast

    def get_xml_ast(self) -> ET.Element:
        if self.xml_ast_:
            return self.xml_ast_
        self.xml_ast_ = self.__read_xml_ast()
        return self.xml_ast_

    def __read_xml_ast(self):
        if not self.xml_ast_:
            with open(self.filename_, 'rt') as f:
                xml_str = f.read()
                return ET.fromstring(xml_str)
        return self.xml_ast_
