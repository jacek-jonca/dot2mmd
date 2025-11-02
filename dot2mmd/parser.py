import re

class DotParser:
    NODE_PATTERN = re.compile(r'(\w+)\s*\[([^\]]+)\]')
    EDGE_PATTERN = re.compile(r'(\w+)\s*->\s*(\w+)(?:\s*\[([^\]]+)\])?')
    SUBGRAPH_PATTERN = re.compile(r'subgraph\s+(\w+)\s*\{([^}]*)\}', re.DOTALL)
    ATTR_PATTERN = re.compile(r'(\w+)\s*=\s*"?(.*?)"?\s*(?:;|$)')

    def __init__(self, dot_text: str):
        self.dot_text = dot_text
        self.nodes = {}
        self.edges = []
        self.subgraphs = {}

    def parse_attributes(self, attr_text: str) -> dict:
        attrs = {}
        for match in self.ATTR_PATTERN.finditer(attr_text):
            key, value = match.groups()
            attrs[key.strip()] = value.strip()
        return attrs

    def parse(self):
        text = self.dot_text

        # Parse subgraphs
        for match in self.SUBGRAPH_PATTERN.finditer(text):
            cluster_name, cluster_body = match.groups()
            self.subgraphs[cluster_name] = cluster_body.strip()
            text = text.replace(match.group(0), '')

        # Parse nodes
        for match in self.NODE_PATTERN.finditer(text):
            node_id, attr_text = match.groups()
            attrs = self.parse_attributes(attr_text)
            self.nodes[node_id] = attrs

        # Parse edges
        for match in self.EDGE_PATTERN.finditer(text):
            source, target, attr_text = match.groups()
            attrs = self.parse_attributes(attr_text) if attr_text else {}
            self.edges.append({
                'from': source,
                'to': target,
                'label': attrs.get('label', ''),
                'dir': attrs.get('dir', 'forward'),
                'style': attrs.get('style', ''),
                'color': attrs.get('color', '')
            })

        return self.nodes, self.edges, self.subgraphs
