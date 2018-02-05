#!/usr/bin/env python2.7

import sys
import json as json
import ast
import jsontree
import asttokens
from xml.sax.saxutils import quoteattr

def PrintUsage():
    sys.stderr.write("""
Usage:
    parse_python.py <file>

""")
    exit(1)

def read_file_to_string(filename):
    f = open(filename, 'rt')
    s = f.read()
    f.close()
    return s


def parse_file(filename):
    global c, d
    tree = asttokens.ASTTokens(read_file_to_string(filename), parse=True).tree

    json_tree = []
    def gen_identifier(identifier, node_type = 'identifier', node=None):
        pos = len(json_tree)
        json_node = {}
        json_tree.append(json_node)
        json_node['type'] = node_type
        json_node['value'] = identifier
        try:
            json_node['line_no'] = str(node.lineno)
            json_node['col'] = str(node.col_offset)
        except:
            try:
                json_node['line_no'] = str(node.first_token.start[0])
                json_node['col'] = str(node.first_token.start[1])
            except:
                pass
        return pos

    def traverse_list(l, node_type = 'list', node = None):
        pos = len(json_tree)
        json_node = {}
        json_tree.append(json_node)
        json_node['type'] = node_type
        try:
                json_node['line_no'] = str(node.lineno)
                json_node['col'] = str(node.col_offset)
        except:
            try:
                json_node['line_no'] = str(node.first_token.start[0])
                json_node['col'] = str(node.first_token.start[1])
            except: pass
        children = []
        for item in l:
            children.append(traverse(item))
        if (len(children) != 0):
            json_node['children'] = children
        return pos

    def traverse(node):
        pos = len(json_tree)
        json_node = {}
        json_tree.append(json_node)
        json_node['type'] = type(node).__name__
        try:
                json_node['line_no'] = str(node.lineno)
                json_node['col'] = str(node.col_offset)
        except:
            try:
                json_node['line_no'] = str(node.first_token.start[0])
                json_node['col'] = str(node.first_token.start[1])
            except: pass
        children = []
        if isinstance(node, ast.Name):
            json_node['value'] = node.id
        elif isinstance(node, ast.Num):
            json_node['value'] = unicode(node.n)
        elif isinstance(node, ast.Str):
            json_node['value'] = node.s.decode('utf-8')
        elif isinstance(node, ast.alias):
            json_node['value'] = unicode(node.name)
            if node.asname:
                children.append(gen_identifier(node.asname, node = node))
        elif isinstance(node, ast.FunctionDef):
            json_node['value'] = unicode(node.name)
        elif isinstance(node, ast.ClassDef):
            json_node['value'] = unicode(node.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                json_node['value'] = unicode(node.module)
        elif isinstance(node, ast.Global):
            for n in node.names:
                children.append(gen_identifier(n, node = node))
        elif isinstance(node, ast.keyword):
            json_node['value'] = unicode(node.arg)


        # Process children.
        if isinstance(node, ast.For):
            children.append(traverse(node.target))
            children.append(traverse(node.iter))
            children.append(traverse_list(node.body, 'body', node))
            if node.orelse:
                children.append(traverse_list(node.orelse, 'orelse', node))
        elif isinstance(node, ast.If) or isinstance(node, ast.While):
            children.append(traverse(node.test))
            children.append(traverse_list(node.body, 'body', node))
            if node.orelse:
                children.append(traverse_list(node.orelse, 'orelse', node))
        elif isinstance(node, ast.With):
            children.append(traverse(node.context_expr))
            if node.optional_vars:
                children.append(traverse(node.optional_vars))
            children.append(traverse_list(node.body, 'body', node))
        elif isinstance(node, ast.TryExcept):
            children.append(traverse_list(node.body, 'body', node))
            children.append(traverse_list(node.handlers, 'handlers', node))
            if node.orelse:
                children.append(traverse_list(node.orelse, 'orelse', node))
        elif isinstance(node, ast.TryFinally):
            children.append(traverse_list(node.body, 'body', node))
            children.append(traverse_list(node.finalbody, 'finalbody', node))
        elif isinstance(node, ast.arguments):
            children.append(traverse_list(node.args, 'args', node))
            children.append(traverse_list(node.defaults, 'defaults', node))
            if node.vararg:
                children.append(gen_identifier(node.vararg, 'vararg', node))
            if node.kwarg:
                children.append(gen_identifier(node.kwarg, 'kwarg', node))
        elif isinstance(node, ast.ExceptHandler):
            if node.type:
                children.append(traverse_list([node.type], 'type', node))
            if node.name:
                children.append(traverse_list([node.name], 'name', node))
            children.append(traverse_list(node.body, 'body', node))
        elif isinstance(node, ast.ClassDef):
            children.append(traverse_list(node.bases, 'bases', node))
            children.append(traverse_list(node.body, 'body', node))
            children.append(traverse_list(node.decorator_list, 'decorator_list', node))
        elif isinstance(node, ast.FunctionDef):
            children.append(traverse(node.args))
            children.append(traverse_list(node.body, 'body', node))
            children.append(traverse_list(node.decorator_list, 'decorator_list', node))
        else:
            # Default handling: iterate over children.
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.expr_context) or isinstance(child, ast.operator) or isinstance(child, ast.boolop) or isinstance(child, ast.unaryop) or isinstance(child, ast.cmpop):
                    # Directly include expr_context, and operators into the type instead of creating a child.
                    json_node['type'] = json_node['type'] + type(child).__name__
                else:
                    children.append(traverse(child))

        if isinstance(node, ast.Attribute):
            children.append(gen_identifier(node.attr, 'attr', node))

        if (len(children) != 0):
            json_node['children'] = children
        return pos

    traverse(tree)
    return json.dumps(json_tree, separators=(',', ':'), ensure_ascii=False)

def write(i, indent_level = 0):
        global lines
        node = tree[i]
        if "value" in node:
            if "line_no" in node:
                if "end_col" in node:
                    lines.append("\t"*indent_level + "<" + node['type'] + ' value=' + quoteEscape(node["value"]) + ' lineno="' + str(node['line_no']) + '" col="' + str(node['col']) + '" end_line_no="' + str(node['end_line_no']) + '" end_col="' + str(node['end_col']) + '">')
                else:
                    lines.append("\t"*indent_level + "<" + node['type'] + ' value=' + quoteEscape(node["value"]) + ' lineno="' + str(node['line_no']) + '" col="' + str(node['col']) + '">')
            else:
                lines.append("\t"*indent_level + "<" + node['type'] + ' value=' + quoteEscape(node["value"]) + '>')
        else:
            if "line_no" in node:
                if "end_col" in node:
                    lines.append("\t"*indent_level + "<" + node['type'] + ' lineno="' + str(node['line_no']) + '" col="' + str(node['col']) + '" end_line_no="' + str(node['end_line_no']) + '" end_col="' + str(node['end_col']) + '">')
                else:
                    lines.append("\t"*indent_level + "<" + node['type'] + ' lineno="' + str(node['line_no']) + '" col="' + str(node['col']) + '">')
            else:
                lines.append("\t"*indent_level + "<" + node['type'] + ">")
        for child in node["children"]:
            write(int(child), indent_level + 1)
        lines.append("\t"*indent_level + "</" + node["type"] + ">")

def quoteEscape(x):
    return quoteattr(x);

def getFirstNonChildInd(tree, index):
    def getHelper(index):
        if len(tree[index]['children']) == 0:
            return index
        return max([getHelper(i) for i in tree[index]['children']])
    return getHelper(index) + 1
def getLast(text, i):
    tree[i]["end_line_no"] = len(text.split('\n'))
    tree[i]["end_col"] = len(text.split('\n')[-1])
def addEnd(tree, i, text):
    try:
        first_non_child = getFirstNonChildInd(tree, i)
        first_non_child_start = tree[first_non_child]["line_no"]
        first_non_child_col = tree[first_non_child]["col"]
        tree[i]["end_line_no"] = int(first_non_child_start)
        tree[i]["end_col"] = int(first_non_child_col)
        if first_non_child_col == "-1":
            tree[first_non_child]["col"] = "0"
            tree[i]["end_col"] = "0"
    except:
        getLast(text, i)
    for child in tree[i]['children']:
        addEnd(tree, child, text)




if __name__ == "__main__":
    try:
        text = open(sys.argv[1], "r+").read()

        json_file = parse_file(sys.argv[1])
        tree = jsontree.JSONTreeDecoder().decode(json_file)

        x = tree[0]

        lines = []
        addEnd(tree, 0, text)
        write(0)

        print('\n'.join(lines))

    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
