import ast
from src.main.python.sundry.merged_types_restorer import _py_node_type_name_to_ast_type


class NodeRestorer:

    def __init__(self, xml_node, py_node):
        """
        Partially restores Python AST node from XML AST node
        :param xml_node: XML AST node from which to restore Python AST node
        :param py_node: Python AST node to restore
        """
        self.xml_node = xml_node
        self.py_node = py_node
        self.xml_node_children = [child for child in xml_node]

    def traverse_name(self):
        self.py_node.id = self.xml_node.attrib['value']

    def traverse_name_constant(self):
        self.py_node.value = self.xml_node.attrib['value']

    def traverse_constant(self):
        self.py_node.value = self.xml_node.attrib['value']

    def traverse_num(self):
        self.py_node.n = self.xml_node.attrib['value']

    def traverse_str(self):
        self.py_node.s = self.xml_node.attrib['value']

    def traverse_alias(self):
        name = self.xml_node.attrib['value']
        as_name = self.xml_node.find('identifier').attrib['value']
        if not hasattr(self.py_node, 'names'):
            name_type = _py_node_type_name_to_ast_type['alias']
            self.py_node.names = [name_type()]
        self.py_node.names[-1].name = name
        self.py_node.names[-1].asname = as_name

    def traverse_function_def(self):
        self.py_node.name = self.xml_node.attrib['value']

    def traverse_except_handler(self):
        if 'value' in self.xml_node.attrib:
            self.py_node.name = self.xml_node.attrib['value']

    def traverse_class_def(self):
        self.py_node.name = self.xml_node.attrib['value']

    def traverse_import_from(self):
        if 'value' in self.xml_node.attrib:
            self.py_node.module = self.xml_node.attrib['value']

    def traverse_global(self):
        self.py_node.names = [elem.attrib['value']
                              for elem in self.xml_node.findall('identifier')]

    def traverse_keyword(self):
        self.py_node.arg = self.xml_node.attrib['value']

    def traverse_arg(self):
        self.py_node.arg = self.xml_node.attrib['value']

    def traverse_tuple(self):
        self.py_node.elts = self._traverse_xml_node_list(xml_node_children)

    def traverse_list(self):
        self.py_node.elts = self._traverse_xml_node_list(xml_node_children)

        # Process children.
    def traverse_assign(self):
        py_node_children = self._traverse_xml_node_list(xml_node_children)
        self.py_node.targets = py_node_children[:-1]
        self.py_node.value = py_node_children[-1]

    def traverse_for(self):
        self.py_node.target = self._traverse(xml_node_children[0])
        self.py_node.iter = self._traverse(xml_node_children[1])
        assert xml_node_children[2].tag == 'body'  # should be body in XML_For layout
        self.py_node.body = [self._traverse(xml_body_item)
                             for xml_body_item in xml_node_children[2]]
