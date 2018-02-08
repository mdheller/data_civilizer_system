Golden Record 
===================

Introduction
----------
Golden Record is an entity consolidation tool, which, given a collection of clusters of duplicate records, constructs a single record for each cluster that contains the canonical value for each attribute. 

Golden Record is written in C++ with a python wrapper.

### Compile

You can either compile the code to a python module or a c++ code.

A. Compile to python module

1. Install SWIG from http://www.swig.org/
2. Creat a python3 virtual enviroment and active it

* python3 -m venv FOO/BAR/
* source FOO/BAR/bin/activate

3. Go to the 'code' folder and execute the following command:

* ./run.sh 

It will produce a file '_goldenrecord.so'_ The call_goldenrecord.py will call the modules in it.

B. Compile to C++ code [OPTIONAL]

1. Run test.py and you will get the executable program enum_rule. DO NOT MAKE IT DIRECTLY FROM MAKE FILE!
2. To run enum_rule, you only need to specify two parameters. The rest 3 are all optional. The first one is a folder contains the input_file. The second one is the attribute name on which you want to run golden record.

The following are all about how to run the python code. 

### Specify Parameters
Golden Record only takes two parameters

* input_file: this parameter is a path to a CSV table that contains a set of records. The table is assumed to have an attribute with the name exactly 'cluster_id'. Records with the same value in this attribute are considered  within the same cluster.

* output_file: this parameter is a path to a file where the golden records will write into.

### Run Golden Record

First import call_goldenrecord and then call the main function in call_goldenrecord. See the jupyter notebook file for an example

### Interaction

It will go throught each column in the input table and ask if you want to run golden record on the column. You will have 5 options:

0 (default): skip,  

1: replacing rule only, 

2: replacing rules + full rules, 

3: replacing rules + deletion rules, 

4: replacing rules + deletion rules + full rules,

5: full rules only

For shorter values (e.g., names) use 2 or 4. For longer values (e.g., full address) use 1 or 3. Note that:

* Replacing rules are the rules like 9 <-> 9th, which is a pair of substrings in a pair of value within the same cluster.

* Deletion rules are the rules with one side as empty.

* Full rules uses a pair of values within the same cluster as a single rule.

If you do not skip the column, it will repeatly generate a group of rules and ask you to choose from:

0: do not apply all of them;  

1: apply them to all;  

2: apply them reversely; 

3: postpone;  

4; exit

The first option skip the rule group. The second replaces the left side with the right side. The third replaces the right side with the left side. The last one will terminate the processing of the current column.

Finally, after go throught all columns, the updated table will write into a CSV file as specified in the parameter.


