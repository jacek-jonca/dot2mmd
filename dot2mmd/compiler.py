"""
Compiles an AST (from ast.py) into a MermaidJS string.
"""
import textwrap
from .ast import (
    Graph,
    Node,
    Edge,
    Subgraph,
    GraphAttribute,
    DefaultAttribute,
)


class MermaidCompiler:
    """
    Compiles a Graph AST node into a MermaidJS string.
    
    Converts DOT features to MermaidJS equivalents where possible.
    """
    
    # Map DOT shapes to MermaidJS bracket types
    SHAPE_MAP = {
        "box": ("[", "]"),
        "rect": ("[", "]"),
        "rectangle": ("[", "]"),
        "polygon": ("[", "]"),  # Best effort
        "ellipse": ("(", ")"),
        "oval": ("(", ")"),
        "circle": ("((", "))"),
        "diamond": ("{", "}"),
        "default": ("[", "]"), # Default if shape is unknown
    }

    def __init__(self):
        self.mmd_lines: list[str] = []
        self.graph_type_str = "graph"  # 'graph' (undirected) or 'flowchart' (directed)
        self.edge_op_str = "---" # '---' (undirected) or '-->' (directed)
        self.rankdir = "TB"  # Default Top-to-Bottom
        
        # Default attribute dictionaries
        self.default_node_attrs: dict[str, str] = {}
        self.default_edge_attrs: dict[str, str] = {}

    def compile(self, graph: Graph) -> str:
        """Main compilation method."""
        self.mmd_lines = []
        
        if graph.type.lower() == "digraph":
            self.graph_type_str = "flowchart" # Mermaid uses 'flowchart' for directed
            self.edge_op_str = "-->"
        
        # 1. Process global attributes first
        for stmt in graph.statements:
            if isinstance(stmt, GraphAttribute):
                if stmt.key.lower() == "rankdir" and stmt.value.lower() == "lr":
                    self.rankdir = "LR"
        
        self.mmd_lines.append(f"{self.graph_type_str} {self.rankdir}")

        # 2. Process default attributes
        for stmt in graph.statements:
            if isinstance(stmt, DefaultAttribute):
                self._process_default_attribute(stmt)

        # 3. Process all other statements
        for stmt in graph.statements:
            self._process_statement(stmt, indent=1)
            
        return "\n".join(self.mmd_lines)

    def _process_statement(self, stmt: object, indent: int = 0):
        """Recursively processes a statement node."""
        indent_str = "    " * indent
        
        if isinstance(stmt, Subgraph):
            self._process_subgraph(stmt, indent)
        elif isinstance(stmt, GraphAttribute):
            # Check for subgraph-specific attributes
            if stmt.key.lower() == "rankdir" and stmt.value.lower() == "lr":
                self.mmd_lines.append(f"{indent_str}direction LR")
        elif isinstance(stmt, DefaultAttribute):
            # These are processed first, but could be scoped in subgraphs.
            # For now, we only handle global defaults.
            pass
        elif isinstance(stmt, Node):
            self._process_node(stmt, indent)
        elif isinstance(stmt, Edge):
            self._process_edge(stmt, indent)

    def _process_default_attribute(self, stmt: DefaultAttribute):
        """Processes a DefaultAttribute statement."""
        if stmt.type == "node":
            self.default_node_attrs.update(stmt.attributes)
        elif stmt.type == "edge":
            self.default_edge_attrs.update(stmt.attributes)

    def _process_node(self, node: Node, indent: int):
        """Processes a Node statement."""
        indent_str = "    " * indent
        
        # Combine default and specific attributes
        final_attrs = self.default_node_attrs.copy()
        final_attrs.update(node.attributes)

        # Mermaid only supports shape and label (via text)
        label = final_attrs.get("label", node.id)
        # Get default shape, fallback to 'box' if none set
        default_shape = self.default_node_attrs.get("shape", "box")
        shape = final_attrs.get("shape", default_shape) 

        # Escape quotes in label
        label = label.replace('"', '#quot;')
        
        # Mermaid doesn't like newlines in the node text,
        # but supports <br> tags.
        label = label.replace("\n", "<br>")

        mermaid_shape = self.SHAPE_MAP.get(shape, self.SHAPE_MAP["default"])
        
        self.mmd_lines.append(
            f'{indent_str}{node.id}{mermaid_shape[0]}"{label}"{mermaid_shape[1]}'
        )

    def _process_edge(self, edge: Edge, indent: int):
        """Processes an Edge statement."""
        indent_str = "    " * indent
        
        # Combine default and specific attributes
        final_attrs = self.default_edge_attrs.copy()
        final_attrs.update(edge.attributes)
        
        label = final_attrs.get("label", "")
        
        # Handle 'dir=back'
        from_node = edge.from_node
        to_node = edge.to_node
        edge_op = self.edge_op_str
        
        if final_attrs.get("dir") == "back":
            from_node, to_node = to_node, from_node
            
        if label:
            # Escape quotes
            label = label.replace('"', '#quot;')
            self.mmd_lines.append(
                f'{indent_str}{from_node} {edge_op}|"{label}"| {to_node}'
            )
        else:
            self.mmd_lines.append(
                f"{indent_str}{from_node} {edge_op} {to_node}"
            )

    def _process_subgraph(self, subgraph: Subgraph, indent: int):
        """Recursively processes a Subgraph statement."""
        indent_str = "    " * indent
        
        is_rank_same = False
        if subgraph.id is None:
            # This is an anonymous subgraph. Check for 'rank=same'.
            for stmt in subgraph.statements:
                if (
                    isinstance(stmt, GraphAttribute)
                    and stmt.key.lower() == "rank"
                    and stmt.value.lower() == "same"
                ):
                    is_rank_same = True
                    break

        if subgraph.id and subgraph.id.lower().startswith("cluster"):
            # This is a Mermaid subgraph
            subgraph_label = subgraph.id.replace("cluster_", "", 1)
            self.mmd_lines.append(f'{indent_str}subgraph "{subgraph_label}"')
            for stmt in subgraph.statements:
                self._process_statement(stmt, indent + 1)
            self.mmd_lines.append(f"{indent_str}end")
            
        elif is_rank_same:
            # This is a { rank=same; ... } block
            node_ids = []
            for stmt in subgraph.statements:
                if isinstance(stmt, Node):
                    # We only need the ID, not the full definition
                    node_ids.append(stmt.id)
            
            if node_ids:
                # We also need to define the nodes, as they might just be
                # 'node_id;' statements
                for stmt in subgraph.statements:
                    if isinstance(stmt, Node):
                         # Process node definitions if they have attributes
                        if stmt.attributes:
                            self._process_node(stmt, indent)

                # Add the rank line
                rank_line = indent_str + "{ rank = same; " + "; ".join(node_ids) + " }"
                # Mermaid docs show 'rank same' but 'rank = same' also works
                # and is safer. Let's try what the docs show.
                rank_line = indent_str + "{ rank same; " + "; ".join(node_ids) + " }"
                self.mmd_lines.append(rank_line)
            
        else:
            # Not a cluster and not rank=same.
            # Process statements at the current indent level.
            for stmt in subgraph.statements:
                self._process_statement(stmt, indent)

