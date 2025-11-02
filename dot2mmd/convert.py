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

def _format_node(node_id: str, label: Optional[str], attrs: Optional[Dict[str, str]] = None) -> str:
    label_text = _safe_label(label or node_id)
    safe_id = re.sub(r"[^A-Za-z0-9_]+", "_", node_id)
    return f"{safe_id}[{label_text}]"

def _format_edge(a: str, b: str, directed: bool, label: Optional[str] = None, attrs: Optional[Dict[str, str]] = None) -> str:
    sep = "-->" if directed else "---"
    a_id = re.sub(r"[^A-Za-z0-9_]+", "_", a)
    b_id = re.sub(r"[^A-Za-z0-9_]+", "_", b)
    
    if label is not None:
        label_text = _safe_label(label.strip())
        return f"{a_id} {sep} |{label_text}| {b_id}"
    else:
        return f"{a_id} {sep} {b_id}"

# -------------------- pydot parser --------------------

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
    for n in g.get_nodes() or []:
        if n.get_name() == "node":
            continue
        node_id = n.get_name().strip('"')
        label = n.get_attributes().get("label", node_id)
        mermaid_lines.append(_format_node(node_id, label))

    # Subgraphs / clusters
    for sg in g.get_subgraphs() or []:
        try:
            sg_name = sg.get_name().strip('"')
        except Exception:
            sg_name = "cluster"
        mermaid_lines.append(f"subgraph {re.sub(r'[^A-Za-z0-9_]+', '_', sg_name)}")
        for n in sg.get_nodes() or []:
            if n.get_name() == "node":
                continue
            node_id = n.get_name().strip('"')
            label = n.get_attributes().get("label", node_id)
            mermaid_lines.append("  " + _format_node(node_id, label))
        mermaid_lines.append("end")

    # Edges
    for e in g.get_edges() or []:
        src = e.get_source().strip('"')
        dst = e.get_destination().strip('"')
        ed_attrs = e.get_attributes() or {}
        label = ed_attrs.get("label")
        mermaid_lines.append(_format_edge(src, dst, is_directed, label, ed_attrs))

    return "\n".join(mermaid_lines)

# -------------------- Simple parser --------------------

_node_line_re = re.compile(r"^\s*([A-Za-z0-9_\-\"<>]+)\s*(\[.*\])?\s*;?\s*$")
_edge_line_re = re.compile(r"^\s*([A-Za-z0-9_\"<>:]+)\s*([-]{1,2}|->|-->)\s*([A-Za-z0-9_\"<>:]+)\s*(\[.*\])?\s*;?\s*$")
_attr_re = re.compile(r"([a-zA-Z0-9_\-]+)\s*=\s*\"?([^\",\\]]+)\"?")

def _parse_attr_block(block: str) -> Dict[str, str]:
    d: Dict[str, str] = {}
    if not block:
        return d
    block = block.strip().lstrip("[").rstrip("]").strip()
    for m in _attr_re.finditer(block):
        key, val = m.group(1), m.group(2)
        d[key.strip()] = val
    return d

def _dot_to_mermaid_simple(dot_text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", dot_text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    directed = False
    attrs_global: Dict[str, str] = {}
    nodes_seen: Dict[str, Dict] = {}
    edges_seen: list = []

    for ln in lines:
        m = re.match(r"^(digraph|graph)\b", ln, re.I)
        if m:
            directed = m.group(1).lower() == "digraph"
            continue
        if ln in ["{", "}"] or ln.endswith("{") or ln.endswith("}"):
            continue
        m_attr = re.match(r"^([A-Za-z0-9_\-]+)\s*=\s*([A-Za-z0-9_\"<>:]+)\s*;?", ln)
        if m_attr:
            key, val = m_attr.group(1), m_attr.group(2).strip('"')
            attrs_global[key] = val
            continue
        m = _edge_line_re.match(ln)
        if m:
            a, op, b = m.group(1).strip('"'), m.group(2), m.group(3).strip('"')
            attrs_block = m.group(4) or ""
            attr_d = _parse_attr_block(attrs_block)
            nodes_seen.setdefault(a, {})
            nodes_seen.setdefault(b, {})
            edges_seen.append((a, b, directed, attr_d))
            continue
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
        label = ad.get('label', n)
        mermaid_lines.append(_format_node(n, label, ad))

    # Edges
    for a, b, directed_flag, ad in edges_seen:
        label = ad.get('label')
        mermaid_lines.append(_format_edge(a, b, directed_flag, label, ad))

    return "\n".join(mermaid_lines)

# -------------------- Public API --------------------

def dot_to_mermaid(dot_text: str_
