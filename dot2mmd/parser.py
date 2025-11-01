"""
Parses DOT language text into an AST using the pyparsing library.
"""

import pyparsing as pp
from . import ast

# --- Grammar Definition ---

# Define punctuation and keywords
LBRACE, RBRACE, LBRACK, RBRACK, SEMI, EQ, COMMA = map(pp.Suppress, "{}[]=;,")
ARROW = pp.Literal("->")
LINE = pp.Literal("--")
GRAPH_KW = pp.CaselessLiteral("graph")
DIGRAPH_KW = pp.CaselessLiteral("digraph")
STRICT_KW = pp.CaselessLiteral("strict")
SUBGRAPH_KW = pp.CaselessLiteral("subgraph")
NODE_KW = pp.CaselessLiteral("node")
EDGE_KW = pp.CaselessLiteral("edge")

# Define basic elements
# An identifier can be a simple name, a number, or a quoted string
identifier = pp.Word(pp.alphanums + "_") | pp.pyparsing_common.number | pp.QuotedString('"') | pp.QuotedString("'")
atom = identifier.copy()

# Attribute lists: [ a=b, c="d" ]
attr_pair = pp.Group(atom + EQ + atom)
attr_list = pp.Group(pp.delimitedList(attr_pair, COMMA))
opt_attr_list = pp.Optional(LBRACK + attr_list + RBRACK, default=[])

# --- Statements ---
stmt = pp.Forward()

# Node statement: node_id [ attr_list ] ;
node_id = atom.copy().setResultsName("id")
node_stmt = (node_id + opt_attr_list.setResultsName("attrs") + pp.Optional(SEMI))

# Edge statement: node_id (->|--) node_id [ attr_list ] ;
edge_op = (ARROW | LINE).setResultsName("op")
edge_rhs = edge_op + node_id
edge_stmt = (node_id + pp.OneOrMore(edge_rhs) + opt_attr_list.setResultsName("attrs") + pp.Optional(SEMI))

# Attribute statement: (graph|node|edge) [ attr_list ] ;
attr_stmt = ((GRAPH_KW | NODE_KW | EDGE_KW).setResultsName("type") +
             LBRACK + attr_list.setResultsName("attrs") + RBRACK + pp.Optional(SEMI))

# Subgraph: [ subgraph [id] ] { stmt_list }
subgraph_id = pp.Optional(SUBGRAPH_KW + pp.Optional(identifier, default=None), default=None)
subgraph = (subgraph_id.setResultsName("id") +
            LBRACE + pp.Group(pp.ZeroOrMore(stmt)).setResultsName("stmts") + RBRACE)

# A statement can be any of the above
stmt <<= pp.Group(attr_stmt | edge_stmt | subgraph | node_stmt)

# Graph: [strict] (graph|digraph) [id] { stmt_list }
graph_type = (GRAPH_KW | DIGRAPH_KW).setResultsName("graph_type")
graph_id = pp.Optional(identifier, default=None).setResultsName("id")
strict = pp.Optional(STRICT_KW, default=None).setResultsName("strict")

graph = (strict +
         graph_type +
         graph_id +
         LBRACE + pp.Group(pp.ZeroOrMore(stmt)).setResultsName("stmts") + RBRACE +
         pp.Optional(pp.StringEnd()))

# --- Parse Actions (to build AST) ---

def _flatten_tokens(tokens):
    """Helper to handle nested groups from pyparsing."""
    if len(tokens) == 1 and isinstance(tokens[0], pp.ParseResults):
        return tokens[0]
    return tokens

def to_dict(tokens):
    """Convert list of [key, value] pairs to a dict."""
    return dict(tokens.asList())

attr_list.setParseAction(to_dict)
attr_stmt.setParseAction(lambda t: ast.Attr(t.type, t.attrs))
node_stmt.setParseAction(lambda t: ast.Node(t.id, t.attrs))

def parse_edge(tokens):
    t = _flatten_tokens(tokens)
    nodes = [t[0]]
    op = "->" # default
    
    # pyparsing groups (op, node) pairs
    for i in range(1, len(t.asList())):
        item = t[i]
        if isinstance(item, str): # An operator
            op = item
        elif isinstance(item, pp.ParseResults) and len(item) == 2: # (op, node)
            op = item[0]
            nodes.append(item[1])
        elif 'attrs' not in t: # a node
             nodes.append(item)

    return ast.Edge(nodes, op, t.attrs)
edge_stmt.setParseAction(parse_edge)


def parse_subgraph(tokens):
    t = _flatten_tokens(tokens)
    subgraph_name = t.id[1] if t.id and len(t.id) > 1 else None
    if not subgraph_name:
        subgraph_name = f"cluster_{hash(str(t.stmts)) % 10000}" # Generate a default ID
    return ast.Subgraph(subgraph_name, t.stmts.asList())
subgraph.setParseAction(parse_subgraph)


def parse_graph(tokens):
    t = _flatten_tokens(tokens)
    graph_node = ast.Graph(t.graph_type, t.id, t.stmts.asList(), strict=(t.strict is not None))
    
    # Separate statements and process global attributes
    final_stmts = []
    for s in graph_node.stmts:
        if isinstance(s, ast.Attr):
            if s.type == 'graph':
                graph_node.graph_attrs.update(s.attrs)
            elif s.type == 'node':
                graph_node.node_attrs.update(s.attrs)
            elif s.type == 'edge':
                graph_node.edge_attrs.update(s.attrs)
        else:
            final_stmts.append(s)
    
    graph_node.stmts = final_stmts
    return graph_node

graph.setParseAction(parse_graph)

# Ignore C-style and Shell-style comments
graph.ignore(pp.cppStyleComment)
graph.ignore(pp.pythonStyleComment)


def parse_dot(text: str) -> ast.Graph:
    """
    Parses a DOT string into an AST.
    
    Args:
        text: The DOT language string.

    Returns:
        An ast.Graph object.
    
    Raises:
        pp.ParseException: If parsing fails.
    """
    try:
        result = graph.parseString(text, parseAll=True)
        return result[0]
    except pp.ParseException as e:
        print(f"Error parsing DOT file:\n{e.loc}\n{e.pstr}\n{' ' * (e.col - 1) + '^'}")
        raise
