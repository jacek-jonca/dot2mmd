"""
Command-line interface for the dot2mmd converter.
"""

import argparse
import sys
from .parser import parse_dot
from .compiler import MermaidCompiler

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Graphviz DOT files to MermaidJS .mmd syntax.",
        epilog="Example: dot2mmd graph.dot -o graph.mmd"
    )
    parser.add_argument(
        "input_file",
        metavar="INPUT",
        type=str,
        help="Input DOT file path. Use '-' for stdin."
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        type=str,
        help="Output .mmd file path. (Default: stdout)"
    )
    
    args = parser.parse_args()

    # Read input
    try:
        if args.input_file == '-':
            dot_content = sys.stdin.read()
        else:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                dot_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Process
    try:
        ast = parse_dot(dot_content)
        compiler = MermaidCompiler()
        mermaid_content = compiler.compile(ast)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Write output
    try:
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_content)
            print(f"Successfully converted '{args.input_file}' to '{args.output_file}'.")
        else:
            sys.stdout.write(mermaid_content)
            
    except IOError as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
