# -------------------- dot2mmd/convert.py --------------------
from __future__ import annotations
import re
from typing import Dict, Optional

try:
    import pydot  # type: ignore
    _HAS_PYDOT = True
except Exception:
    pydot = None
    _HAS_PYDOT = False

__all__ = ["dot_to_mermaid"]

# -------------------- Helpers --------------------
def _safe_label(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = s.strip()
    if s == "":
        return ""
    s = s.replace('"', '\\"')
    if re.search(r"\s|<|>", s):
        return f'"{s}"'
    return s

def _map_rankdir(attrs: Dict[str, str]) -> str:
    rd = attrs.get("rankdir", "TB").upper()
    return rd if rd in ("LR", "RL", "TB") else "TB"

def _format_edge(a: str, b: str, directed: bool, label: Optional[str] = None) -> str:
    sep = "-->" if directed else "---"
    a_id = re.sub(r"[^A-Za-z0-9_]+", "_", a)
    b_id = re.sub(r"[^A-Za-z0-9_]+", "_", b)
    if label:
        return f"{a_id} {sep} |{label.strip()}| {b_id}"
    return f"{a_id} {sep} {b_id}"

# -------------------- Simple parser --------------------
def _parse_attr_block(block: str) -> Dict[str, str]:
    d: Dict[str, str] = {}
    if not block:
        return d
    block = block.strip().lstrip("[").rstrip("]").strip()
    for part in block.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, val = part.split("=", 1)
            d[key.strip()] = val.strip().strip('"')
    return d

def _dot_to_mermaid_simple(dot_text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", dot_text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    directed = False
    nodes: Dict[str, Dict[str, str]] = {}
    edges: list = []

    node_line_re = re.compile(r"^([A-Za-z0-9_]+)\s*(\[(.*?)\])?\s*;?$")
    edge_line_re = re.compile(r"^([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)\s*(\[(.*?)\])?\s*;?$")

    for ln in lines:
        m_node = node_line_re.match(ln)
        m_edge = edge_line_re.match(ln)
        if m_node and not m_edge:
            name, _, attr_block = m_node.groups()
            nodes[name] = {}
            if attr_block:
                nodes[name].update(_parse_attr_block(attr_block))
        elif m_edge:
            src, dst, _, attr_block = m_edge.groups()
            attrs = {}
            if attr_block:
                attrs.update(_parse_attr_block(attr_block))
            edges.append((src, dst, attrs))

    mermaid_lines = ["graph TB"]
    shape_map = {"oval": "[{}]", "box": "[{}]", "diamond": "{{{}}}"}

    # Nodes
    for n, ad in nodes.items():
        label = ad.get("label", n).replace("\n", "\\n")
        shape = ad.get("shape", "oval")
        fmt = shape_map.get(shape, "[{}]")
        mermaid_lines.append(f"{n}{fmt.format(label)}")

    # Edges
    for src, dst, ad in edges:
        label = ad.get("label")
        mermaid_lines.append(_format_edge(src, dst, directed=True, label=label))

    return "\n".join(mermaid_lines)

# -------------------- Pydot parser --------------------
def _dot_to_mermaid_pydot(dot_text: str) -> str:
    if not _HAS_PYDOT:
        raise RuntimeError("pydot is not installed")
    graphs = pydot.graph_from_dot_data(dot_text)
    if not graphs:
        raise ValueError("pydot could not parse DOT input")
    g = graphs[0]

    is_directed = g.get_type() == "digraph"
    attrs = g.get_attributes() or {}
    rankdir = _map_rankdir(attrs)
    mermaid_lines: list[str] = [f"graph {rankdir}"]

    # Nodes
    shape_map = {"diamond": "{{{}}}", "oval": "[{}]", "box": "[{}]"}
    for n in g.get_nodes() or []:
        if n.get_name() == "node":
            continue
        node_id = n.get_name().strip('"')
        label = n.get_attributes().get("label", node_id).replace("\n", "\\n")
        shape = n.get_attributes().get("shape", "oval").lower()
        fmt = shape_map.get(shape, "[{}]")
        mermaid_lines.append(f"{node_id}{fmt.format(label)}")

    # Edges
    for e in g.get_edges() or []:
        src = e.get_source().strip('"')
        dst = e.get_destination().strip('"')
        label = e.get_attributes().get("label")
        mermaid_lines.append(_format_edge(src, dst, is_directed, label))

    return "\n".join(mermaid_lines)

# -------------------- Public API --------------------
def dot_to_mermaid(dot_text: str, prefer_pydot: bool = True) -> str:
    dot_text = dot_text.strip()
    if not dot_text:
        raise ValueError("Empty DOT text")

    if prefer_pydot and _HAS_PYDOT:
        try:
            return _dot_to_mermaid_pydot(dot_text)
        except Exception:
            return _dot_to_mermaid_simple(dot_text)

    return _dot_to_mermaid_simple(dot_text)
