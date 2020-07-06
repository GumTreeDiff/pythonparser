import os
import pytest
from xml.etree import ElementTree as ET
from src.main.python.pythonparser_3 import *

_input_dir = "src/test/python/inputs/code_samples/"


@pytest.mark.parametrize(
    "test_input_dirs",
    [
        _input_dir + "small_samples",

        _input_dir + "big_samples",

        _input_dir + "class_samples",

        _input_dir + "corner_cases_samples",

        pytest.param(_input_dir + "fstring_samples",
                     marks=pytest.mark.skip(reason='fstrings are not supported yet')),

        pytest.param(_input_dir + "python_3_8_samples",
                     marks=pytest.mark.skip(reason='python 3.8 not supported yet'))
    ]
)
def test_produce_valid_xml(test_input_dirs):
    """
    :arg: list of input dirs (pytest parametrize)
    Checks if parser producing valid xml file
    :return: None
    """

    for entry in os.scandir(test_input_dirs):
        print(f'Current entry is: {entry.path}')
        parsed_json = parse_file(entry.path)
        xml_str = json2xml(parsed_json)
        try:
            _ = ET.fromstring(xml_str)
        except ET.ParseError as e:
            pytest.fail(f"test file: {entry.path}, ET.ParseError msg: {e}")


@pytest.mark.parametrize(
    "test_input_dirs",
    [
        (_input_dir + "non_valid_python_code_samples")
    ]
)
def test_non_valid_python_code(test_input_dirs):
    """
    Checks behaviour on non valid python code inputs.
    Expected behaviour: SyntaxError is thrown during parsing

    :return: None
    """
    for entry in os.scandir(test_input_dirs):
        print(f'Current entry is: {entry.path}')
        with pytest.raises(SyntaxError) as exc_info:
            _ = parse_file(entry.path)
        assert "invalid syntax" in str(exc_info.value)


@pytest.mark.parametrize(
    "input_file_paths,"
    "expected,"
    "xml_elements",
    [
        (
            _input_dir + "small_samples/small_3.py",
            (
             {"lineno": "1",  "col": "0",  "end_line_no": "21", "end_col": "63"},
             {"lineno": "13", "col": "18", "end_line_no": "13", "end_col": "27"},
             {"lineno": "13", "col": "18", "end_line_no": "13", "end_col": "22"}
            ),
            (
             "FunctionDef",
             "BinOpLShift",
             "SubscriptLoad"
            )
        )
    ]
)
def test_correct_token_params(input_file_paths, expected, xml_elements):
    """
    :args: from parametrize
    Checks if token parameters such as 'lineno',
    'col', 'end_line_no', 'end_col' obtained by parser correctly.

    :return: None
    """
    parsed_json = parse_file(input_file_paths)
    xml_str = json2xml(parsed_json)
    root = ET.fromstring(xml_str)
    assert len(expected) == len(xml_elements), "Incorrect test setting, len(expected) " \
                                               "should be the same as len(description)"
    for exp, x_elem in zip(expected, xml_elements):
        match = root.find(".//" + x_elem)
        assert match is not None
        match_params = match.attrib
        assert all(exp[key] == match_params[key] for key in exp.keys())


@pytest.mark.parametrize(
    "input_file_paths,"
    "expected",
    [
        (
            _input_dir + "small_samples/small_2.py",
            {"Assign": 2,  "Call": 2,  "Import": 1, "FunctionDef": 0}
        ),
        (
            _input_dir + "small_samples/small_4.py",
            {"Assign": 3,  "AugAssignAdd": 1,  "For": 4, "ListLoad": 12}
        )
    ]
)
def test_all_tokens_are_accounted_for(input_file_paths, expected):
    """
    Checks that all tokens such as Assign, Call,.. etc
    are accounted for by parser
    :return: None
    """
    parsed_json = parse_file(input_file_paths)
    xml_str = json2xml(parsed_json)
    root = ET.fromstring(xml_str)
    assert all(len(root.findall(".//" + token)) == expected[token]
               for token in expected.keys())


@pytest.mark.parametrize(
    "input_file_paths,"
    "expected",
    [
        (
            _input_dir + "small_samples/small_2.py",
            {"NameStore": 2,  "NameLoad": 4, "AttributeStore": 0, "AttributeLoad": 1}
        ),
        (
            _input_dir + "small_samples/small_3.py",
            {"NameStore": 5,  "NameLoad": 13, "AttributeStore": 0, "AttributeLoad": 3}
        )
    ]
)
def test_merge_expr_context_and_ops_into_type(input_file_paths, expected):
    """
    Checks that parser correctly include expr_context and operators
    into the type instead of creating a child
    :return: None
    """
    parsed_json = parse_file(input_file_paths)
    xml_str = json2xml(parsed_json)
    root = ET.fromstring(xml_str)
    assert all(len(root.findall(".//" + token)) == expected[token]
               for token in expected.keys())
