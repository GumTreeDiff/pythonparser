#!/usr/bin/env python3

# Copyright (c) Aniskov N.

import sys
sys.path.append('../../../..')

import argparse
import ast
import logging
import xml.etree.ElementTree as ET

import astor

from src.main.python.inverse_parser._node_restorer import _NodeRestorer
from src.main.util.const import LOGGER_NAME
from src.main.util.file_util import get_content_from_file, create_file
from src.main.util.log_util import log_and_raise_error

logger = logging.getLogger(LOGGER_NAME)


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
            log_and_raise_error('Either "filename" or "xml_str" must not be None.',
                                logger,
                                ValueError)

        if filename and xml_str:
            log_and_raise_error('Only one of the "filename" and "xml_str" must be provided. Not both.',
                                logger,
                                ValueError)

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
        generated_src = astor.to_source(py_ast)
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
        xml_str = get_content_from_file(filename, to_strip_nl=False)
        self.xml_ast_ = ET.fromstring(xml_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse AST of python3 code in XML format to source code')
    parser.add_argument('filename', type=str, help='XML file with AST')
    parser.add_argument('-o', '--output_file',
                        help='The name of the file '
                             'where the generated code will be written'
                        )

    args = parser.parse_args()

    inverse_parser = InverseParser(args.filename)
    gen_src = inverse_parser.get_source()

    if args.output_file is not None:
        create_file(gen_src, args.output_file)

    else:
        print(gen_src)
