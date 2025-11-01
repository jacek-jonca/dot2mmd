from __future__ import annotations
_node_line_re = re.compile(r"^\s*([A-Za-z0-9_\-\"<>]+)\s*(\[.*\])?\s*;?\s*$")
_edge_line_re = re.compile(r"^\s*([A-Za-z0-9_\"<>:]+)\s*([-]{1,2}|->|-->)\s*([A-Za-z0-9_\"<>:]+)\s*(\[.*\])?\s*;?\s*$")
_attr_re = re.compile(r"([a-zA-Z0-9_\-]+)\s*=\s*\"?([^\",\]]+)\"?")

def _parse_attr_block(block: str) -> Dict[str, str]:
d: Dict[str, str] = {}
if not block:
return d
block = block.strip().lstrip("[").rstrip("]").strip()
for m in _attr_re.finditer(block):
key, val = m.group(1), m.group(2)
d[key.strip()] = val.strip()
return d

def _dot_to_mermaid_simple(dot_text: str) -> str:
# Remove comments
text = re.sub(r"/\*.*?\*/", "", dot_text, flags=re.DOTALL)
text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

directed = False
attrs_global: Dict[str, str] = {}
nodes_seen: Dict[str, Dict] = {}

current_subgraph: List[str] = []

for ln in lines:
# Detect graph type
m = re.match(r"^(digraph|graph)\b", ln, re.I)
if m:
directed = m.group(1).lower() == "digraph"
continue
# Skip braces
if ln in ["{", "}"] or ln.endswith("{") or ln.endswith("}"):
continue
# Detect attributes
m_attr = re.match(r"^([A-Za-z0-9_\-]+)\s*=\s*([A-Za-z0-9_\"<>:]+)\s*;?", ln)
if m_attr:
key, val = m_attr.group(1), m_attr.group(2).strip('"')
attrs_global[key] = val
continue
# Edge lines with optional ports (node:port)
m = _edge_line_re.match(ln)
if m:
a, op, b = m.group(1).strip('"'), m.group(2), m.group(3).strip('"')
attrs_block = m.group(4) or ""
attr_d = _parse_attr_block(attrs_block)
nodes_seen.setdefault(a, {})
nodes_seen.setdefault(b, {})
nodes_seen.setdefault('_edges', []).append((a, b, directed, attr_d))
continue
# Node line
m = _node_line_re.match(ln)
if m:
name = m.group(1).strip('"')
block = m.group(2) or ""
attr_d = _parse_attr_block(block)
nodes_seen.setdefault(name, {}).update(attr_d)
continue

rankdir = _map_rankdir(attrs_global)
mermaid_lines = [f"graph {rankdir}"]

# Nodes
for n, ad in nodes_seen.items():
if n == '_edges':
continue
label = ad.get('label', n)
mermaid_lines.append(_format_node(n, label, ad))

# Edges
for a, b, directed_flag, ad in nodes_seen.get('_edges', []):
label = ad.get('label')
mermaid_lines.append(_format_edge(a, b, directed_flag, label, ad))

return '\n'.join(mermaid_lines)


def dot_to_mermaid(dot_text: str, prefer_pydot: bool = True) -> str:
dot_text = dot_text.strip()
if not dot_text:
raise ValueError("Empty DOT text")


if prefer_pydot and _HAS_PYDOT:
return _dot_to_mermaid_pydot(dot_text)


return _dot_to_mermaid_simple(dot_text)

def test_simple_edge():
dot = "digraph { A -> B }"
mmd = dot_to_mermaid(dot)
assert "graph TD" in mmd
assert "A --> B" in mmd

def test_undirected_graph():
dot = "graph { A -- B }"
mmd = dot_to_mermaid(dot)
assert "graph TD" in mmd
assert "A --- B" in mmd

def test_label_preserved():
dot = "digraph { A -> B [label=\"hi\"] }"
mmd = dot_to_mermaid(dot)
assert "A -->|hi| B" in mmd

def test_subgraph_cluster():
dot = "digraph { subgraph cluster_0 { A; B } C; A -> C }"
mmd = dot_to_mermaid(dot)
assert "subgraph cluster_0" in mmd
assert "A --> C" in mmd

def test_rankdir_lr():
dot = "digraph { rankdir=LR; A -> B }"
mmd = dot_to_mermaid(dot)
assert "graph LR" in mmd

def test_rankdir_rl():
dot = "digraph { rankdir=RL; A -> B }"
mmd = dot_to_mermaid(dot)
assert "graph RL" in mmd

def test_node_with_spaces():
dot = 'digraph { "Node 1" -> "Node 2" }'
mmd = dot_to_mermaid(dot)
assert 'Node_1 --> Node_2' in mmd

def test_html_label():
dot = 'digraph { A -> B [label="<b>Bold</b>"] }'
mmd = dot_to_mermaid(dot)
assert 'A -->|<b>Bold</b>| B' in mmd
