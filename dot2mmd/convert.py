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

# -------------------- Simple parser --------------------
def _dot_to_mermaid_simple(dot_text: str) -> str:
    # Remove comments
    dot_text = re.sub(r"/\*.*?\*/", "", dot_text, flags=re.DOTALL)
    dot_text = re.sub(r"//.*?$", "", dot_text, flags=re.MULTILINE)

    statements = [s.strip() for s in dot_text.split(";") if s.strip()]
    nodes: Dict[str, Dict[str, str]] = {}
    edges = []

    shape_map = {"oval": "[{}]", "diamond": "{{{}}}"}

    for stmt in statements:
        # Node
        m_node = re.match(r"^(\w+)\s*\[(.*)\]$", stmt)
        if m_node:
            name, attr_block = m_node.groups()
            nodes[name] = _parse_attr_block(attr_block)
            continue

        # Edge
        m_edge = re.match(r"^(\w+)\s*->\s*(\w+)\s*\[(.*)\]$", stmt)
        if m_edge:
            src, dst, attr_block = m_edge.groups()
            edges.append((src, dst, _parse_attr_block(attr_block)))
            continue

    mermaid_lines = ["graph TB"]

    for src, dst, ed_attrs in edges:
        # Source node
        src_attr = nodes.get(src, {})
        src_label = src_attr.get("label", src).replace("\n", "\\n")
        src_shape = shape_map.get(src_attr.get("shape", "oval"), "[{}]")
        src_node = f"{src}{src_shape.format(src_label)}"

        # Destination node
        dst_attr = nodes.get(dst, {})
        dst_label = dst_attr.get("label", dst).replace("\n", "\\n")
        dst_shape = shape_map.get(dst_attr.get("shape", "oval"), "[{}]")
        dst_node = f"{dst}{dst_shape.format(dst_label)}"

        # Edge label
        edge_label = ed_attrs.get("label")
        if edge_label:
            mermaid_lines.append(f"{src_node} --> |{edge_label.strip()}| {dst_node}")
        else:
            mermaid_lines.append(f"{src_node} --> {dst_node}")

    return "\n".join(mermaid_lines)

# -------------------- Pydot parser --------------------
def _dot_to_mermaid_pydot(dot_text: str) -> str:
    if not _HAS_PYDOT:
        raise RuntimeError("pydot is not installed")
    graphs = pydot.graph_from_dot_data(dot_text)
    if not graphs:
        raise ValueError("pydot could not parse DOT input")
    g = graphs[0]

    shape_map = {"diamond": "{{{}}}", "oval": "[{}]", "box": "[{}]"}

    # Collect nodes
    nodes: Dict[str, Dict[str, str]] = {}
    for n in g.get_nodes() or []:
        if n.get_name() == "node":
            continue
        node_id = n.get_name().strip('"')
        nodes[node_id] = n.get_attributes()

    mermaid_lines: list[str] = ["graph TB"]

    # Collect edges
    for e in g.get_edges() or []:
        src = e.get_source().strip('"')
        dst = e.get_destination().strip('"')
        ed_attrs = e.get_attributes() or {}

        src_attr = nodes.get(src, {})
        dst_attr = nodes.get(dst, {})

        src_label = src_attr.get("label", src).replace("\n", "\\n")
        src_shape = shape_map.get(src_attr.get("shape", "oval"), "[{}]")
        dst_label = dst_attr.get("label", dst).replace("\n", "\\n")
        dst_shape = shape_map.get(dst_attr.get("shape", "oval"), "[{}]")

        src_node = f"{src}{src_shape.format(src_label)}"
        dst_node = f"{dst}{dst_shape.format(dst_label)}"

        edge_label = ed_attrs.get("label")
        if edge_label:
            mermaid_lines.append(f"{src_node} --> |{edge_label.strip()}| {dst_node}")
        else:
            mermaid_lines.append(f"{src_node} --> {dst_node}")

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
