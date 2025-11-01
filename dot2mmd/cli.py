import sys, argparse
from .convert import dot_to_mermaid

def cli(argv=None) -> int:
p = argparse.ArgumentParser(prog="dot2mmd", description="Convert DOT to Mermaid .mmd")
p.add_argument("input")
p.add_argument("-o", "--output")
p.add_argument("--no-pydot", dest="use_pydot", action="store_false")
args = p.parse_args(argv)

if args.input == "-":
dot_text = sys.stdin.read()
in_name = None
else:
with open(args.input, "r", encoding="utf-8") as f:
dot_text = f.read()
in_name = args.input

mermaid = dot_to_mermaid(dot_text, prefer_pydot=args.use_pydot)

out = args.output
if out is None and in_name:
out = in_name[:-4] + ".mmd" if in_name.lower().endswith(".dot") else in_name + ".mmd"

if out:
with open(out, "w", encoding="utf-8") as f:
f.write(mermaid)
print(f"Wrote {out}")
else:
print(mermaid)
return 0

if __name__ == "__main__":
raise SystemExit(cli())
