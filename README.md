DOT to MermaidJS Converterdot2mmd is a Python utility to convert graph files from the Graphviz DOT language to MermaidJS (.mmd) syntax.This is a best-effort conversion, as the DOT language is significantly more complex than Mermaid. It supports a common subset of features:

graph and digraph
Node definitions with label and shape (box, ellipse, diamond, circle)
Edge definitions with label
Subgraphs (prefixed with cluster_)
Global graph, node, and edge attributes
rankdir=LR for Left-to-Right layout

Installation

You must have Python 3.7+ installed.Clone this repository or download the source code.Navigate to the directory containing setup.py.Install the package using pip:# To install the package:
pip install .

# For development (editable install):
pip install -e .

This will install the package and its dependency (pyparsing) and add the dot2mmd command to your shell's path.UsageYou can use the tool from the command line.dot2mmd [INPUT_FILE] -o [OUTPUT_FILE]

ArgumentsINPUT_FILE: The path to the input .dot file. Use - to read from stdin.-o, --output [OUTPUT_FILE]: The path to the output .mmd file. If omitted, the result will be printed to stdout.Examples1. Convert a file to another file:dot2mmd my_graph.dot -o my_graph.mmd

2. Convert a file to print to console:dot2mmd my_graph.dot

3. Use with pipes (stdin/stdout):cat my_graph.dot | dot2mmd -

