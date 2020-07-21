from xml.etree import ElementTree as ET
from src.main.python.pythonparser.pythonparser_3 import *

_test_dir = "src/test/python/"

if __name__ == '__main__':
    path_to_file = "/src/test/resources/pythonparser_3/inputs/code_samples/" \
                   "case_small_code_snippets/small_3.py"
    parsed_json = parse_file(path_to_file)
    xml_str = json2xml(parsed_json)
    print(xml_str)
    tree = ET.fromstring(xml_str)
    res = tree.findall(".//NameLoad")
    print(len(res))