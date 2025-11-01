"""
Parses DOT language strings into an Abstract Syntax Tree (AST).

Uses the pyparsing library to define the grammar.
"""
import pyparsing as pp
from .ast import (
    Graph,
    Node,
    Edge,
    Subgraph,
    GraphAttribute,
    DefaultAttribute,
)

# --- Grammar Constants ---
LBRACE, RBRACE, LBRACK, RBRACK, EQ, SEMI = map(pp.Suppress, "{}[]=;")
ID = pp.Word(pp.alphas + "_", pp.alphanums + "_")

# --- Grammar Definition ---

# Attribute lists: [attr=value; attr=value] or [attr=value, attr=value]
# DOT allows comma or semicolon.
attr_val = pp.QuotedString('"') | pp.QuotedString("'") | ID
attr_pair = pp.Group(ID + EQ + attr_val)
attr_list = (
    LBRACK
    + pp.Optional(  # Add Optional in case of empty list []
        pp.delimitedList(
            attr_pair,
            delim=pp.oneOf("; ,"),  # Delimiter is not optional
            allow_trailing_delim=True,  # <-- This is the main fix
        )
    )
    + RBRACK
).setResultsName("attributes")

# Node definition: node_id [attr_list];
# Also handles simple node declarations: node_id; (for rank=same)
node_id = ID.setResultsName("id")
node_stmt = pp.Group(
    node_id + pp.Optional(attr_list) + SEMI
).setResultsName("node_stmt")

# Edge definition: node_id -> node_id [attr_list];
edge_op = pp.oneOf("-> --").setResultsName("op")
edge_stmt = pp.Group(
    node_id.setResultsName("from_node")
    + edge_op
    + node_id.setResultsName("to_node")
    + pp.Optional(attr_list)
    + SEMI
).setResultsName("edge_stmt")

# Default Attribute Statements
# node [attr_list];
# edge [attr_list];
# graph [attr_list];
default_attr_type = pp.oneOf("graph node edge", caseless=True).setResultsName("type")
default_attr_stmt = pp.Group(
    default_attr_type + attr_list + SEMI
).setResultsName("default_attr")

# Subgraph: subgraph [id] { stmt_list }
# Also supports anonymous subgraphs: { stmt_list }
subgraph = pp.Forward()

# Global graph attributes: rankdir=LR;
graph_attr_stmt = pp.Group(
    ID.setResultsName("key") + EQ + ID.setResultsName("value") + SEMI
).setResultsName("graph_attr")

# A statement can be a node, edge, subgraph, default attr, or global attribute
stmt = default_attr_stmt | graph_attr_stmt | node_stmt | edge_stmt | subgraph

# List of statements
stmt_list = pp.ZeroOrMore(stmt)

# Subgraph definition
subgraph_header = pp.Keyword("subgraph", caseless=True)
subgraph_id = pp.Optional(ID).setResultsName("id")
subgraph_body = LBRACE + stmt_list + RBRACE
# An anonymous subgraph is just a body, for rank=same etc.
anonymous_subgraph_body = (
    LBRACE + stmt_list + RBRACE
).setResultsName("anonymous_body")
# A subgraph can be named or anonymous
subgraph <<= pp.Group(
    (subgraph_header + subgraph_id + subgraph_body) | anonymous_subgraph_body
).setResultsName("subgraph")


# Graph definition: [strict] [di]graph [id] { stmt_list }
strict = pp.Optional(pp.Keyword("strict", caseless=True)).setResultsName("strict")
graph_type = pp.oneOf("graph digraph", caseless=True).setResultsName("type")
graph_id = pp.Optional(ID).setResultsName("id")
graph_body = LBRACE + stmt_list + RBRACE

graph = pp.Group(
    strict + graph_type + graph_id + graph_body
).setResultsName("graph")

# --- Parse Actions ---
# Assign parse actions to convert to AST nodes
graph.setParseAction(Graph.from_parse_result)
subgraph.setParseAction(Subgraph.from_parse_result)
node_stmt.setParseAction(Node.from_parse_result)
edge_stmt.setParseAction(Edge.from_parse_result)
graph_attr_stmt.setParseAction(GraphAttribute.from_parse_result)
default_attr_stmt.setParseAction(DefaultAttribute.from_parse_result)

# Set common pyparsing settings for efficiency
pp.ParserElement.enablePackrat()


def parse_dot(dot_string: str) -> Graph:
    """
    Parses a DOT language string into an AST.
    """
    try:
        # Parse the string. Use parseString to get the first (and only) result.
        parsed_graph = graph.parseString(dot_string, parseAll=True)[0]
        return parsed_graph
    except pp.ParseException as e:
        # Provide a more helpful error message
        print(f"Error parsing DOT file at line {e.lineno}, col {e.col}:")
        print(e.line)
        print(f"{(e.col - 1) * ' '}^")
        raise ValueError(f"Error during conversion: {e.msg}") from e


