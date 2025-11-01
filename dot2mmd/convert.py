import pytest
from dot2mmd.convert import dot_to_mermaid

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
