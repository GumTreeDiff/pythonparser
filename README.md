# Pythonparser

[![elena-lyulina](https://circleci.com/gh/elena-lyulina/pythonparser/tree/master.svg?style=shield)](https://app.circleci.com/pipelines/github/elena-lyulina/pythonparser?branch=master)

This repository contains parsers from **python code** to **xml/json** and vice versa.
There are parsers for **python2** (see [pythonparser](src/main/python/pythonparser-2.py), source code from 
[GumTreeDiff pythonparser](https://github.com/GumTreeDiff/pythonparser) repository) and 
**python3** (see [pythonparser3](src/main/python/pythonparser-3.py), source code from [pythonparser](https://github.com/Varal7/pythonparser) repository  and [150k Python Dataset](https://eth-sri.github.io/py150) project). 

We are going to support Python 3.8 in **python3** parser:
- [ ] [the "walrus" operator](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions);
- [ ] [positional-only parameters](https://docs.python.org/3/whatsnew/3.8.html#positional-only-parameters);
- [ ] [f-strings assignment](https://docs.python.org/3/whatsnew/3.8.html#f-strings-support-for-self-documenting-expressions-and-debugging);

[Here](https://docs.python.org/3/whatsnew/3.8.html) you can read about all new features that Python 3.8 provides.


### Installation
- python2:  
    `pip install -r requirements.txt`
  
- python3:  
    `pip3 install -r requirements.txt`  
- python3 tests:
    `pip3 install -r requirements-test.txt` 

### Run parser
- python2:  
    `python pythonparser_2 path_to_src_file.py`
  
- python3:  
    `python3 pythonparser_3 path_to_src_file.py`

To run tests for pythonparser_3:

`python3 -m pytest`

### Examples

This section describes several examples of `pythonparser3` work.

<details><summary>First example</summary>

<p>

``` python
a = 5
b = 16.5
print(a + b)
```

</p>

<p>

``` xml
<Module lineno="1" col="0" end_line_no="3" end_col="12">
	<Assign lineno="1" col="0" end_line_no="1" end_col="5">
		<Name_Store value="a" lineno="1" col="0" end_line_no="1" end_col="1">
		</Name_Store>
		<Constant value="5" value_type="int" lineno="1" col="4" end_line_no="1" end_col="5">
		</Constant>
	</Assign>
	<Assign lineno="2" col="0" end_line_no="2" end_col="8">
		<Name_Store value="b" lineno="2" col="0" end_line_no="2" end_col="1">
		</Name_Store>
		<Constant value="16.5" value_type="float" lineno="2" col="4" end_line_no="2" end_col="8">
		</Constant>
	</Assign>
	<Expr lineno="3" col="0" end_line_no="3" end_col="12">
		<Call lineno="3" col="0" end_line_no="3" end_col="12">
			<Name_Load value="print" lineno="3" col="0" end_line_no="3" end_col="5">
			</Name_Load>
			<BinOp_Add lineno="3" col="6" end_line_no="3" end_col="11">
				<Name_Load value="a" lineno="3" col="6" end_line_no="3" end_col="7">
				</Name_Load>
				<Name_Load value="b" lineno="3" col="10" end_line_no="3" end_col="11">
				</Name_Load>
			</BinOp_Add>
		</Call>
	</Expr>
</Module>
```

</p>

</details>


<details><summary>Second example</summary>

<p>

``` python 
# Test example

from ast import NodeVisitor


class Example(NodeVisitor):
    def generic_visit(self, node):
        print(type(node).__name__)
        NodeVisitor.generic_visit(self, node)
```

</p>

<p>

``` xml 
<Module lineno="1" col="0" end_line_no="9" end_col="45">
	<ImportFrom value="ast" lineno="3" col="0" end_line_no="3" end_col="27" import_level="0">
		<alias value="NodeVisitor" lineno="3" col="0" end_line_no="3" end_col="4">
		</alias>
	</ImportFrom>
	<ClassDef value="Example" lineno="6" col="0" end_line_no="9" end_col="45">
		<bases lineno="6" col="0" end_line_no="9" end_col="45">
			<Name_Load value="NodeVisitor" lineno="6" col="14" end_line_no="6" end_col="25">
			</Name_Load>
		</bases>
		<keywords lineno="6" col="0" end_line_no="9" end_col="45">
		</keywords>
		<body lineno="6" col="0" end_line_no="9" end_col="45">
			<FunctionDef value="generic_visit" lineno="7" col="4" end_line_no="9" end_col="45">
				<arguments lineno="7" col="22" end_line_no="7" end_col="32">
					<posonlyargs lineno="7" col="22" end_line_no="7" end_col="32">
					</posonlyargs>
					<args lineno="7" col="22" end_line_no="7" end_col="32">
						<arg value="self" lineno="7" col="22" end_line_no="7" end_col="26">
						</arg>
						<arg value="node" lineno="7" col="28" end_line_no="7" end_col="32">
						</arg>
					</args>
					<kwonlyargs lineno="7" col="22" end_line_no="7" end_col="32">
					</kwonlyargs>
					<kw_defaults lineno="7" col="22" end_line_no="7" end_col="32">
					</kw_defaults>
					<defaults lineno="7" col="22" end_line_no="7" end_col="32">
					</defaults>
				</arguments>
				<body lineno="7" col="4" end_line_no="9" end_col="45">
					<Expr lineno="8" col="8" end_line_no="8" end_col="34">
						<Call lineno="8" col="8" end_line_no="8" end_col="34">
							<Name_Load value="print" lineno="8" col="8" end_line_no="8" end_col="13">
							</Name_Load>
							<Attribute_Load lineno="8" col="14" end_line_no="8" end_col="33">
								<Call lineno="8" col="14" end_line_no="8" end_col="24">
									<Name_Load value="type" lineno="8" col="14" end_line_no="8" end_col="18">
									</Name_Load>
									<Name_Load value="node" lineno="8" col="19" end_line_no="8" end_col="23">
									</Name_Load>
								</Call>
								<attr value="__name__" lineno="8" col="14" end_line_no="8" end_col="33">
								</attr>
							</Attribute_Load>
						</Call>
					</Expr>
					<Expr lineno="9" col="8" end_line_no="9" end_col="45">
						<Call lineno="9" col="8" end_line_no="9" end_col="45">
							<Attribute_Load lineno="9" col="8" end_line_no="9" end_col="33">
								<Name_Load value="NodeVisitor" lineno="9" col="8" end_line_no="9" end_col="19">
								</Name_Load>
								<attr value="generic_visit" lineno="9" col="8" end_line_no="9" end_col="33">
								</attr>
							</Attribute_Load>
							<Name_Load value="self" lineno="9" col="34" end_line_no="9" end_col="38">
							</Name_Load>
							<Name_Load value="node" lineno="9" col="40" end_line_no="9" end_col="44">
							</Name_Load>
						</Call>
					</Expr>
				</body>
				<decorator_list lineno="7" col="4" end_line_no="9" end_col="45">
				</decorator_list>
			</FunctionDef>
		</body>
		<decorator_list lineno="6" col="0" end_line_no="9" end_col="45">
		</decorator_list>
	</ClassDef>
</Module>
```

</p>

</details>

### Tree format

This section describes format of tree, that pythonparser-3 produces.  

Produced tree is a valid XML document. Each node in the document corresponds to a node
of Python AST. It is necessary to note several nuances of the format:  
1. Operations are directly included into node tag. They follow the `underscore` character.

    <details><summary>Example</summary>
	
    <p>

    Node with `BinOp_Add` tag is `BinOp` (binary operation) node
    and operation of that node is addition.
    
    </p>

    </details>
2. [Expression context](https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Load) 
is directly included into node tag. It follows the `underscore` character.
 
    <details><summary>Example</summary>
    
    <p>

    Node with `Name_Load` tag is `Name` node
    and the context of that `Name` is `Load`, which means that we "load" or "read" the
    content holden by `Name` node
    
    </p>
    
    </details>
3. Attributes `lineno`, `col`, `end_line_no`, `end_col` exist in order to determine the position of the token.
4. Nodes that represent constants (`Constant`, `Num`, `Str`) have 
attribute `value_type`, which stores the type of the constant.
5. `ImportFrom` node has attribute `import_level`, which stores integer,
 [level of import](https://greentreesnakes.readthedocs.io/en/latest/nodes.html#ImportFrom).
 
