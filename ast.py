"""
Defines the Abstract Syntax Tree (AST) nodes for the DOT language.
These classes represent the structure of a parsed DOT file.
"""

class ASTNode:
    """Base class for all AST nodes."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

class Graph(ASTNode):
    """Represents a graph or digraph."""
    def __init__(self, graph_type, graph_id, stmts, strict=False):
        self.graph_type = graph_type.lower() # 'graph' or 'digraph'
        self.id = graph_id
        self.stmts = stmts
        self.strict = strict
        # Global attributes
        self.graph_attrs = {}
        self.node_attrs = {}
        self.edge_attrs = {}

class Subgraph(ASTNode):
    """Represents a subgraph."""
    def __init__(self, subgraph_id, stmts):
        self.id = subgraph_id
        self.stmts = stmts

class Node(ASTNode):
    """Represents a node definition (e.g., 'a [label="Node A"]')."""
    def __init__(self, node_id, attrs):
        self.id = node_id
        self.attrs = attrs

class Edge(ASTNode):
    """Represents an edge definition (e.g., 'a -> b [label="Edge"]')."""
    def __init__(self, nodes, edge_op, attrs):
        self.nodes = nodes # List of node IDs, e.g., ['a', 'b', 'c'] for a -> b -> c
        self.op = edge_op # '->' or '--'
        self.attrs = attrs

class Attr(ASTNode):
    """Represents a global attribute statement (e.g., 'graph [rankdir=LR]')."""
    def __init__(self, attr_type, attrs):
        self.type = attr_type.lower() # 'graph', 'node', or 'edge'
        self.attrs = attrs
