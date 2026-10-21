#!/usr/bin/env python3
"""Convert every Mermaid diagram in Markdown docs into standalone d3blocks HTML pages.

Usage:
  python convert_docs.py <path>... --out <dir> [--dark-mode auto|true|false]

Each <path> is a folder (searched for .md, .markdown, .mmd and .mermaid files; .git,
node_modules and the output folder are skipped) or a single file. Every ```mermaid block in a
Markdown file, and the whole of a .mmd / .mermaid file, is one diagram:

  flowchart / graph / flowchart-elk / stateDiagram(-v2)  -> d3.flowgraph
  sequenceDiagram                                        -> d3.sequence
  erDiagram                                              -> d3.erd
  any other kind (gantt, classDiagram, pie, ...)         -> skipped (listed, not an error)

Writes <out>/<source path without suffix>/<n>_<type>.html per diagram (n: the diagram's number
among the Mermaid blocks in its file) and <out>/manifest.json. Errors name the source file and
line. Exit code 1 when a supported diagram fails, else 0.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from d3blocks import D3Blocks
from d3blocks.flowgraph import Flowgraph

# Same pattern as d3blocks' Flowgraph.read_mermaid (test_convert_docs.py keeps them in step).
BLOCK = re.compile(r"^[ \t]*```+[ \t]*mermaid[^\n]*\n(.*?)^[ \t]*```", re.S | re.M)
MARKDOWN = (".md", ".markdown")
MERMAID = (".mmd", ".mermaid")
SKIP_DIRS = {".git", "node_modules"}
TYPES = {
    **{k: ("flowgraph", "flowchart") for k in Flowgraph.FLOWCHART_KINDS},
    **{k: ("flowgraph", "state") for k in Flowgraph.STATE_KINDS},
    "sequenceDiagram": ("sequence", "sequence"),
    "erDiagram": ("erd", "erd"),
}
COUNTS = {
    "flowgraph": {"nodes": "nodes", "edges": "edges", "groups": "groups"},
    "sequence": {"participants": "participants", "messages": "messages", "regions": "groups"},
    "erd": {"entities": "entities", "relationships": "relationships"},
}


def find_blocks(text):
    """[(start line, block text)] for every ```mermaid block; the start line is the first line inside the fence."""
    return [(text.count("\n", 0, m.start(1)) + 1, m.group(1)) for m in BLOCK.finditer(text)]


def kind_of(text):
    """The diagram keyword: the first word of the first line that is not blank or a %% comment."""
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("%%"):
            return line.split()[0]
    return ""


def block_type(text):
    """'flowgraph', 'sequence' or 'erd' for a supported diagram, else None."""
    return TYPES.get(kind_of(text), (None, None))[0]


def source_files(path, out):
    """Files to read under `path`, as (file, its path relative to the parent of `path`)."""
    path = Path(path).resolve()
    base = path.parent
    if not path.exists():
        raise ValueError("%s does not exist" % path)
    if path.is_file():
        if path.suffix.lower() not in MARKDOWN + MERMAID:
            raise ValueError("%s is not a Markdown (.md, .markdown) or Mermaid (.mmd, .mermaid) file" % path)
        return [(path, path.relative_to(base))]
    files = []
    for f in sorted(path.rglob("*")):
        parts = set(f.relative_to(path).parts[:-1])
        if not f.is_file() or f.suffix.lower() not in MARKDOWN + MERMAID or parts & SKIP_DIRS:
            continue
        if out in f.parents:
            continue
        files.append((f, f.relative_to(base)))
    return files


def counts(html, block):
    """Element counts read from the page's JSON payload."""
    m = re.search(r'<script type="application/json" id="\w+-data">(.*?)</script>', html, re.S)
    data = json.loads(m.group(1).replace("<\\/", "</"))
    out = {name: len(data.get(key) or []) for name, key in COUNTS[block].items()}
    if block == "erd":
        out["columns"] = sum(len(e.get("columns") or []) for e in data["entities"])
    return out


def convert(paths, out, dark_mode="auto"):
    """Convert the diagrams under `paths`; return the manifest rows."""
    out = Path(out).resolve()
    rows = []
    for path in paths:
        for file, rel in source_files(path, out):
            text = file.read_text(encoding="utf-8")
            blocks = find_blocks(text) if file.suffix.lower() in MARKDOWN else [(1, text)]
            for n, (line, block) in enumerate(blocks, 1):
                rows.append(convert_block(block, n, line, rel, out, dark_mode))
    return rows


def convert_block(block, n, line, rel, out, dark_mode):
    source = rel.as_posix()
    kind = kind_of(block)
    btype, label = TYPES.get(kind, (None, None))
    row = {"source": source, "block": n, "line": line, "kind": kind, "block_type": btype,
           "status": "skipped", "output": None, "counts": None, "error": None, "error_line": None}
    if btype is None:
        return row
    d3 = D3Blocks(frame=False, verbose="error", support=None)
    try:
        html = getattr(d3, btype)(block, title="%s - %s %d" % (rel.stem, label, n), dark_mode=dark_mode,
                                  filepath=None, showfig=False, return_html=True)
    except ValueError as e:
        # d3blocks names the line inside the block; translate it to the line in the file.
        m = re.search(r"\bline (\d+)", str(e))
        row["error_line"] = line + int(m.group(1)) - 1 if m else line
        row.update(status="error", error="%s:%d: %s" % (source, row["error_line"], e))
        return row
    target = out / rel.with_suffix("") / ("%d_%s.html" % (n, label))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    row.update(status="ok", output=target.relative_to(out).as_posix(), counts=counts(html, btype))
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="folders or files with Mermaid diagrams")
    ap.add_argument("--out", required=True, help="output folder for the HTML pages and manifest.json")
    ap.add_argument("--dark-mode", default="auto", choices=("auto", "true", "false"),
                    help="initial theme of the pages (default: auto, follows the OS)")
    args = ap.parse_args(argv)
    dark_mode = {"auto": "auto", "true": True, "false": False}[args.dark_mode]

    try:
        rows = convert(args.paths, args.out, dark_mode)
    except ValueError as e:
        print("convert_docs: %s" % e, file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    status = [r["status"] for r in rows]
    print("%d rendered, %d skipped, %d errors -> %s" % (status.count("ok"), status.count("skipped"),
                                                       status.count("error"), out / "manifest.json"))
    for r in rows:
        if r["status"] == "skipped":
            print("skipped %s block %d: '%s' has no d3blocks block" % (r["source"], r["block"], r["kind"]))
        elif r["status"] == "error":
            print("error   %s" % r["error"])
    return 1 if "error" in status else 0


if __name__ == "__main__":
    sys.exit(main())
