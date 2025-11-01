"""
Defines the Abstract Syntax Tree (AST) nodes for the DOT language parser.
"""
from __future__ import annotations
import pyparsing as pp


class Node:
    """AST node for a node definition (e.g., node_id [label="..."])."""

    def __init__(self, id: str, attributes: dict[str, str]):
        self.id = id
        self.attributes = attributes

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> Node:
        """Factory method to create a Node from parse results."""
        token = tokens[0]
        attr_dict = {}
        # attributes might be a list or a single result
        if "attributes" in token:
            attrs = token["attributes"]
            if isinstance(attrs, pp.ParseResults):
                for attr in attrs:
                    attr_dict[attr[0]] = attr[1]
        
        return Node(id=token["id"], attributes=attr_dict)

    def __repr__(self) -> str:
        return f"Node(id={self.id}, attributes={self.attributes})"


class Edge:
    """AST node for an edge definition (e.g., a -> b [label="..."])."""

    def __init__(
        self, from_node: str, to_node: str, op: str, attributes: dict[str, str]
    ):
        self.from_node = from_node
        self.to_node = to_node
        self.op = op
        self.attributes = attributes

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> Edge:
        """Factory method to create an Edge from parse results."""
        token = tokens[0]
        attr_dict = {}
        if "attributes" in token:
            attrs = token["attributes"]
            if isinstance(attrs, pp.ParseResults):
                for attr in attrs:
                    attr_dict[attr[0]] = attr[1]

        return Edge(
            from_node=token["from_node"],
            to_node=token["to_node"],
            op=token["op"],
            attributes=attr_dict,
        )

    def __repr__(self) -> str:
        return f"Edge({self.from_node} {self.op} {self.to_node})"


class GraphAttribute:
    """AST node for a global graph attribute (e.g., rankdir=LR)."""

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> GraphAttribute:
        """Factory method to create a GraphAttribute from parse results."""
        token = tokens[0]
        return GraphAttribute(key=token["key"], value=token["value"])

    def __repr__(self) -> str:
        return f"GraphAttribute(key={self.key}, value={self.value})"


class DefaultAttribute:
    """AST node for default attributes (e.g., node [shape=box])."""

    def __init__(self, type: str, attributes: dict[str, str]):
        self.type = type  # 'graph', 'node', or 'edge'
        self.attributes = attributes

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> "DefaultAttribute":
        """Factory method to create a DefaultAttribute from parse results."""
        token = tokens[0]
        attr_dict = {}
        # attributes might be a list or a single result
        if "attributes" in token:
            attrs = token["attributes"]
            if isinstance(attrs, pp.ParseResults):
                for attr in attrs:
                    attr_dict[attr[0]] = attr[1]
        
        return DefaultAttribute(type=token["type"], attributes=attr_dict)

    def __repr__(self) -> str:
        return f"DefaultAttribute(type={self.type}, attributes={self.attributes})"


class Subgraph:
    """AST node for a subgraph."""

    def __init__(self, id: str | None, statements: list):
        self.id = id
        self.statements = statements

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> "Subgraph":
        """Factory method to create a Subgraph from parse results."""
        token = tokens[0]
        statements = []

        # Handle anonymous subgraph body { ... }
        # or named subgraph [subgraph, id, [stmt, ...]]
        
        subgraph_id = token.get("id")
        
        # Find the statement list
        stmt_list_tokens = None
        if "anonymous_body" in token:
            # This is an anonymous subgraph { ... }
            stmt_list_tokens = token["anonymous_body"]
        else:
            # This is a named subgraph subgraph [id] { ... }
            # Look for the list of tokens after 'subgraph' and optional 'id'
            for t in token:
                if isinstance(t, pp.ParseResults):
                    stmt_list_tokens = t
                    break
        
        if stmt_list_tokens:
            for stmt in stmt_list_tokens:
                if isinstance(
                    stmt, (Node, Edge, Subgraph, GraphAttribute, DefaultAttribute)
                ):
                    statements.append(stmt)

        return Subgraph(id=subgraph_id, statements=statements)

    def __repr__(self) -> str:
        return f"Subgraph(id={self.id}, statements={len(self.statements)})"


class Graph:
    """Top-level AST node for a graph."""

    def __init__(self, type: str, id: str | None, statements: list):
        self.type = type
        self.id = id
        self.statements = statements

    @staticmethod
    def from_parse_result(tokens: pp.ParseResults) -> Graph:
        """Factory method to create a Graph from parse results."""
        token = tokens[0]
        statements = []

        # The statements are the last item in the group,
        # which is a ParseResults object
        if token and isinstance(token[-1], pp.ParseResults):
            token_list = token[-1]
            for stmt in token_list:
                if isinstance(
                    stmt,
                    (
                        Node,
                        Edge,
                        Subgraph,
                        GraphAttribute,
                        DefaultAttribute,
                    ),
                ):
                    statements.append(stmt)
        return Graph(
            type=token["type"], id=token.get("id"), statements=statements
        )

    def __repr__(self) -> str:
        return f"Graph(type={self.type}, id={self.id}, statements={len(self.statements)})"

