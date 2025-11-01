"""
Compiles an AST into MermaidJS syntax.
"""

from . import ast

class MermaidCompiler:
    """
    Visits AST nodes and compiles them into a Mermaid .mmd string.
    """
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.graph_type = 'graph' # 'graph' or 'digraph'
        self.global_node_attrs = {}
        self.global_edge_attrs = {}

    def _indent(self, s: str) -> str:
        """Indents a string by the current indent level."""
        return "  " * self.indent_level + s

    def _format_label(self, label: str) -> str:
        """Formats a label for Mermaid, quoting if necessary."""
        # Mermaid needs quotes if there are spaces, parens, or other special chars
        if not label:
            return '""'
        if any(c in label for c in ' ()[]{}"\''):
            # Escape existing quotes
            label = label.replace('"', '#quot;')
            return f'"{label}"'
        return label
    
    def _get_node_shape(self, node_id: str, attrs: dict) -> str:
        """Converts DOT shape to Mermaid shape."""
        label = attrs.get('label', node_id)
        label = self._format_label(label)
        
        shape = attrs.get('shape', self.global_node_attrs.get('shape', 'ellipse'))
        shape = shape.lower()

        if shape in ('box', 'rect', 'rectangle'):
            return f"[{label}]"
        if shape == 'diamond':
            return f"{{{label}}}"
        if shape == 'circle':
            # Mermaid 'circle' shape is `((label))`
            return f"(({label}))"
        if shape in ('ellipse', 'oval'):
            # Mermaid 'stadium' shape is `([label])`
            # We'll use default `(label)` for ellipse
             return f"({label})"
        
        # Default (includes 'plaintext', 'none', etc.)
        return f'["{label}"]' # Use quotes to be safe

    def compile(self, graph: ast.Graph) -> str:
        """Main compilation entry point."""
        self.output = []
        self.indent_level = 0
        self._visit(graph)
        return "\n".join(self.output)

    def _visit(self, node: ast.ASTNode):
        """Generic visit method (visitor pattern)."""
        method_name = f'_visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self._visit_default)
        return visitor(node)

    def _visit_default(self, node: ast.ASTNode):
        """Fallback for unhandled AST nodes."""
        print(f"Warning: No visitor found for {node.__class__.__name__}")

    def _visit_Graph(self, node: ast.Graph):
        self.graph_type = node.graph_type
        self.global_node_attrs = node.node_attrs
        self.global_edge_attrs = node.edge_attrs
        
        # Check for layout direction
        direction = "TD" # Top-Down default
        if node.graph_attrs.get('rankdir', '').upper() == 'LR':
            direction = "LR" # Left-Right
            
        self.output.append(f"graph {direction}")
        self.indent_level += 1
        
        for stmt in node.stmts:
            self._visit(stmt)
            
        self.indent_level -= 1

    def _visit_Subgraph(self, node: ast.Subgraph):
        # Mermaid subgraph IDs don't need 'cluster_' prefix
        sub_id = node.id.replace("cluster_", "")
        self.output.append(self._indent(f"subgraph {sub_id}"))
        self.indent_level += 1
        
        for stmt in node.stmts:
            self._visit(stmt)
            
        self.indent_level -= 1
        self.output.append(self._indent("end"))

    def _visit_Node(self, node: ast.Node):
        shape_str = self._get_node_shape(node.id, node.attrs)
        self.output.append(self._indent(f"{node.id}{shape_str}"))

    def _visit_Edge(self, node: ast.Edge):
        # Determine operator
        op = "-->" if node.op == "->" else "---"
        
        # Check for label
        attrs = {**self.global_edge_attrs, **node.attrs}
        label_str = ""
        if 'label' in attrs:
            label = self._format_label(attrs['label'])
            label_str = f'|{label}|'
            
        # Unroll edge chains (e.g., a -> b -> c)
        for i in range(len(node.nodes) - 1):
            left = node.nodes[i]
            right = node.nodes[i+1]
            self.output.append(self._indent(f"{left} {op}{label_str} {right}"))
