# dot2mmd

Convert Graphviz DOT files to MermaidJS `.mmd` syntax.

## Features

- Converts directed (`digraph`) and undirected (`graph`) DOT graphs to MermaidJS flowcharts.
- Supports node and edge labels, including HTML-like labels.
- Subgraphs (clusters) are converted to Mermaid `subgraph` blocks.
- Detects and applies `rankdir` (TB, LR, RL) to adjust Mermaid direction.
- Optional `pydot` support for robust DOT parsing.
- Fallback parser handles common DOT syntax if `pydot` is not installed.

## Limitations

- Complex DOT constructs (ports, HTML tables, shapes beyond simple rectangles) may not fully convert.
- Mermaid styling beyond labels (colors, shapes) is not preserved.
- Only supports flowchart diagrams; sequence diagrams or other Mermaid types are not supported.

## Installation

```bash
pip install .
# With pydot support for full DOT compatibility
pip install .[pydot]
```

## CLI Usage

```bash
# Convert a DOT file to a Mermaid file
python -m dot2mmd input.dot -o output.mmd

# Use stdin and stdout
cat input.dot | python -m dot2mmd - > output.mmd

# CLI script usage if installed
dot2mmd input.dot -o output.mmd
```

## Python API

```python
from dot2mmd import dot_to_mermaid

dot_source = """
digraph {
    A -> B [label="Edge"]
    subgraph cluster_0 {
        C; D;
    }
}
"""

mermaid_str = dot_to_mermaid(dot_source)
print(mermaid_str)
```

## Tests

Run tests using `pytest`:

```bash
pytest
```

### Example tests include:
- Directed and undirected edges
- Node labels with spaces
- Edge labels and HTML labels
- Subgraph/cluster support
- Rankdir detection (TB, LR, RL)

## Notes

- Works best with `pydot` installed.
- Mermaid output is a flowchart by default.
- Multi-word node labels are automatically quoted.
- Designed for lightweight conversion; not all Graphviz features are supported.
