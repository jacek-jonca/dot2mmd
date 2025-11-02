from .parser import DotParser

SHAPE_MAPPING = {
    "diamond": "{%s}",
    "ellipse": "(%s)",
    "circle": "(%s)",
    "box": "[%s]",
    "rect": "[%s]",
    "rectangle": "[%s]"
}

STYLE_MAPPING = {
    "dashed": "-->",
    "dotted": "-.->",
    "bold": "==>",
    "solid": "-->"
}

class Dot2Mermaid:
    def __init__(self, dot_text: str, graph_type: str = "graph TD"):
        self.dot_text = dot_text
        self.graph_type = graph_type
        self.parser = DotParser(dot_text)
        self.node_classes = {}
        self.edge_classes = {}

    def node_to_mermaid(self, node_id: str, attrs: dict) -> str:
        label = attrs.get('label', node_id)
        shape = attrs.get('shape', 'ellipse').lower()
        template = SHAPE_MAPPING.get(shape, "(%s)")
        mermaid_node = template % label

        # Node color
        color = attrs.get('color')
        if color:
            class_name = f"node_{node_id}"
            self.node_classes[class_name] = color
            mermaid_node += f":::{class_name}"
        return mermaid_node

    def edge_to_mermaid(self, edge: dict, node_map: dict, edge_index: int) -> str:
        from_node = node_map.get(edge['from'], edge['from'])
        to_node = node_map.get(edge['to'], edge['to'])
        label = f" |{edge['label']}| " if edge['label'] else ""
        style = STYLE_MAPPING.get(edge.get('style', 'solid'), '-->')
        if edge.get('dir', 'forward') == 'both':
            style = "<" + style.strip('-=') + ">"
        mermaid_edge = f"{from_node} {style}{label}{to_node}"

        # Edge color
        color = edge.get('color')
        if color:
            class_name = f"edge_{edge_index}"
            self.edge_classes[class_name] = color
            mermaid_edge += f":::{class_name}"
        return mermaid_edge

    def convert_nodes(self, nodes: dict) -> dict:
        return {nid: self.node_to_mermaid(nid, attrs) for nid, attrs in nodes.items()}

    def convert_edges(self, edges: list, node_map: dict) -> list:
        return [self.edge_to_mermaid(edge, node_map, i) for i, edge in enumerate(edges)]

    def generate_class_defs(self) -> list:
        lines = []
        for class_name, color in self.node_classes.items():
            lines.append(f"class {class_name} fill:{color},stroke:{color}")
        for class_name, color in self.edge_classes.items():
            lines.append(f"class {class_name} stroke:{color}")
        return lines

    def convert(self) -> str:
        nodes, edges, subgraphs = self.parser.parse()
        mermaid_lines = [self.graph_type]

        node_map = self.convert_nodes(nodes)
        mermaid_lines.extend(self.convert_edges(edges, node_map))

        # Subgraphs
        for cluster_name, cluster_body in subgraphs.items():
            mermaid_lines.append(f'    subgraph {cluster_name}')
            sub_converter = Dot2Mermaid(cluster_body, graph_type="")
            sub_mermaid = sub_converter.convert()
            for line in sub_mermaid.splitlines():
                mermaid_lines.append(f"        {line}" if line else "")
            mermaid_lines.append('    end')

        # Class definitions
        mermaid_lines.extend(self.generate_class_defs())

        return '\n'.join(mermaid_lines)
