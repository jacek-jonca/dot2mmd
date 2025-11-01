# -------------------- dot2mmd/cli.py --------------------
import sys
import argparse
from .convert import dot_to_mermaid

def cli(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="dot2mmd", description="Convert DOT to Mermaid .mmd")
    parser.add_argument("input", help="Input DOT file or '-' for stdin")
    parser.add_argument("-o", "--output", help="Output .mmd file")
    parser.add_argument("--no-pydot", dest="use_pydot", action="store_false", help="Disable pydot parser")
    args = parser.parse_args(argv)

    # Read DOT input
    if args.input == "-":
        dot_text = sys.stdin.read()
        in_name = None
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            dot_text = f.read()
        in_name = args.input

    # Convert to Mermaid
    mermaid = dot_to_mermaid(dot_text, prefer_pydot=args.use_pydot)

    # Determine output path
    out_path = args.output
    if out_path is None and in_name:
        out_path = in_name[:-4] + ".mmd" if in_name.lower().endswith(".dot") else in_name + ".mmd"

    # Write or print output
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(f"Wrote {out_path}")
    else:
        print(mermaid)

    return 0

if __name__ == "__main__":
    raise SystemExit(cli())
