# pythonparser
[![elena-lyulina](https://circleci.com/gh/elena-lyulina/pythonparser/tree/master.svg?style=shield)](https://app.circleci.com/pipelines/github/elena-lyulina/pythonparser?branch=master)

This repository contains parsers from **python code** to **xml/json** and vice versa.
There are parsers for **python2** (see [pythonparser](src/main/python/pythonparser-2.py), source code from [this](https://github.com/GumTreeDiff/pythonparser) repository) and **python3** (see [pythonparser3](src/main/python/pythonparser-3.py), source code from [this](https://github.com/Varal7/pythonparser) repository  and [this](https://eth-sri.github.io/py150) project). 

We are going to support Python 3.8 in **python3** parser:
- [ ] [the "walrus" operator](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions);
- [ ] [positional-only parameters](https://docs.python.org/3/whatsnew/3.8.html#positional-only-parameters);
- [ ] [f-strings assignment](https://docs.python.org/3/whatsnew/3.8.html#f-strings-support-for-self-documenting-expressions-and-debugging);

[Here](https://docs.python.org/3/whatsnew/3.8.html) you can read about all new features that Python 3.8 provides.


## Installation
- python2:  
    `pip install -r requirements.txt`
  
- python3:  
    `pip3 install -r requirements.txt`  
- python3 tests:
    `pip3 install -r requirements-test.txt` 

## Run parser
- python2:  
    `python pythonparser_2 path_to_src_file.py`
  
- python3:  
    `python3 pythonparser_3 path_to_src_file.py`
## Run tests for pythonparser_3  
`python3 -m pytest`

## EXAMPLES

### Python source code -> XML

<details><summary>First example</summary>

<p>

``` python class:"lineNo"
a = 5
b = 16.5
print(a + b)
```

</p>

<p>

``` xml class:"lineNo"
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


## TODO:
- add some info about tree format
