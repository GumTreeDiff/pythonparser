# Copyright (c) Aniskov N.

from xml.etree import ElementTree as ET
from astmonkey import visitors
import ast

from src.main.python.pythonparser.pythonparser_3 import parse_file, json2xml
from src.main.python.inverse_parser.helpers.merged_types_restorer import MergedTypesRestorer
from src.main.python.inverse_parser.helpers.node_restorer import NodeRestorer


py_node_type_name_to_ast_type_ = \
    dict([(name, cls) for name, cls in ast.__dict__.items() if isinstance(cls, type)])


class InverseParser:
    """
    Class contaning converts AST in XML format to Python AST object
    """
    def __init__(self, filename: str):
        """
        :param filename: path to file containing AST in XML format
        """
        self.filename_ = filename
        self.xml_ast_ = None
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
            self.xml_ast_ = self._read_xml_ast()

        py_ast = self._traverse(self.xml_ast_)
        return py_ast

    def get_xml_ast(self) -> ET.Element:
        if self.xml_ast_:
            return self.xml_ast_
        self.xml_ast_ = self._read_xml_ast()
        return self.xml_ast_

    def _traverse(self, xml_node) -> ast.AST:

        py_node_type, merged_types = MergedTypesRestorer.get_types_from_tag(xml_node)
        py_node = py_node_type()
        self._localize(xml_node, py_node)
        MergedTypesRestorer.set_ctx_and_ops(py_node, merged_types)

        xml_node_children = [child for child in xml_node]

        if xml_node.tag.startswith('Name'):
            py_node.id = xml_node.attrib['value']

        elif xml_node.tag.startswith('NameConstant'):
            py_node.value = xml_node.attrib['value']

        elif xml_node.tag.startswith('Constant'):
            py_node.value = xml_node.attrib['value']

        elif xml_node.tag.startswith('Num'):
            py_node.n = xml_node.attrib['value']

        elif xml_node.tag.startswith('Str'):
            py_node.s = xml_node.attrib['value']

        elif xml_node.tag.startswith('alias'):
            name = xml_node.attrib['value']
            as_name = xml_node.find('identifier').attrib['value']
            if not hasattr(py_node, 'names'):
                name_type = py_node_type_name_to_ast_type_['alias']
                py_node.names = [name_type()]
            py_node.names[-1].name = name
            py_node.names[-1].asname = as_name

        elif xml_node.tag.startswith('FunctionDef'):
            py_node.name = xml_node.attrib['value']

        elif xml_node.tag.startswith('ExceptHandler'):
            if 'value' in xml_node.attrib:
                py_node.name = xml_node.attrib['value']

        elif xml_node.tag.startswith('ClassDef'):
            py_node.name = xml_node.attrib['value']

        elif xml_node.tag.startswith('ImportFrom'):
            if 'value' in xml_node.attrib:
                py_node.module = xml_node.attrib['value']

        elif xml_node.tag.startswith('Global'):
            py_node.names = [elem.attrib['value'] for elem in xml_node.findall('identifier')]

        elif xml_node.tag.startswith('keyword'):
            py_node.arg = xml_node.attrib['value']

        elif xml_node.tag.startswith('arg'):
            py_node.arg = xml_node.attrib['value']

        elif xml_node.tag.startswith('Tuple'):
            py_node.elts = self._traverse_xml_node_list(xml_node_children)

        elif xml_node.tag.startswith('List'):
            py_node.elts = self._traverse_xml_node_list(xml_node_children)

        # Process children.
        if xml_node.tag == 'Assign':
            py_node_children = self._traverse_xml_node_list(xml_node_children)
            py_node.targets = py_node_children[:-1]
            py_node.value = py_node_children[-1]

        elif xml_node.tag == 'For':
            py_node.target = self._traverse(xml_node_children[0])
            py_node.iter = self._traverse(xml_node_children[1])
            assert xml_node_children[2].tag == 'body'  # should be body in XML_For layout
            py_node.body = [self._traverse(xml_body_item) for xml_body_item in xml_node_children[2]]

        elif xml_node_children and ('body' in py_node._fields) and not hasattr(py_node, 'body'):  # TODO: write some defualt handler
            py_node.body = [self._traverse(xml_node_child) for xml_node_child in xml_node_children]

        return py_node

    def _read_xml_ast(self):
        if not self.xml_ast_:
            with open(self.filename_, 'rt') as f:
                xml_str = f.read()
                return ET.fromstring(xml_str)
        return self.xml_ast_

    def _localize(self, xml_node, py_node):
        py_node.col_offset = int(xml_node.attrib['col'])
        py_node.end_col_offset = int(xml_node.attrib['end_col'])
        py_node.lineno = int(xml_node.attrib['lineno'])
        py_node.end_lineno = int(xml_node.attrib['end_lineno'])


def main():
    src_filename = 'src/main/python/sundry/samples/python_code/sample1.py'
    xml_filename = 'src/main/python/sundry/samples/xml_ast_repr/sample1.xml'
    xml_str = json2xml(parse_file(src_filename))
    with open(xml_filename, 'w') as f:
        f.write(xml_str)

    inverse_parser = InverseParser(xml_filename)
    py_ast = inverse_parser.get_py_ast()
    print(inverse_parser.get_source())


if __name__ == '__main__':
    main()
