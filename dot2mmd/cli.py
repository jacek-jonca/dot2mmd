import argparse
from .converter import Dot2Mermaid

def main():
    parser = argparse.ArgumentParser(
        description="Convert Graphviz DOT files to MermaidJS .mmd with full styling, nested subgraphs, and colors"
    )
    parser.add_argument("input", help="Path to DOT input file")
    parser.add_argument("-o", "--output", help="Path to output Mermaid file", default="output.mmd")
    parser.add_argument("-g", "--graph", help="Graph type (graph TD, graph LR, etc.)", default="graph TD")

    args = parser.parse_args()

    # Read input DOT file
    try:
        with open(args.input, "r") as f:
            dot_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Convert using enhanced Dot2Mermaid
    converter = Dot2Mermaid(dot_text, graph_type=args.graph)
    try:
        mermaid_text = converter.convert()
    except Exception as e:
        print(f"Error converting DOT to Mermaid: {e}")
        return

    # Write output file
    try:
        with open(args.output, "w") as f:
            f.write(mermaid_text)
        print(f"Mermaid file successfully written to '{args.output}'")
    except Exception as e:
        print(f"Error writing output file: {e}")
