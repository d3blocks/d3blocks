---
name: d3blocks-docs-diagrams
description: Convert the Mermaid diagrams in a repository's Markdown docs (and .mmd / .mermaid files) into standalone, interactive D3Blocks HTML pages, and report every diagram that fails with its file and line. Use when the user wants to render, convert, migrate or replace all the Mermaid diagrams in their docs (flowcharts, state, sequence or ER diagrams) with interactive pages. Not for making a single chart from data; use the d3blocks skill for that.
metadata:
  Github: D3Blocks
  version: "1.0.0"
---

# D3Blocks docs diagrams

Turns every Mermaid diagram in a set of docs into one self-contained, interactive HTML page
(pan and zoom, search, hover highlighting, dark/light theme, SVG/PNG export), with a manifest
that lists what was converted, skipped or failed.

Requires d3blocks 2.3.0 or later: `pip install -U d3blocks`.

## Steps

1. **Convert.** Run the bundled script on the docs folders (or single files):

   ```bash
   python scripts/convert_docs.py docs/ --out diagrams/
   ```

   It reads `.md` / `.markdown` files (every ```` ```mermaid ```` block) and `.mmd` / `.mermaid`
   files (the whole file), skipping `.git`, `node_modules` and the output folder. Each diagram
   becomes `diagrams/<source path without suffix>/<n>_<type>.html`, where `n` numbers the
   Mermaid blocks in that file. `--dark-mode` sets the initial theme: `auto` (default, follows
   the OS), `true` or `false`.

   | Mermaid | Rendered with |
   |---|---|
   | `flowchart`, `graph`, `flowchart-elk` | `d3.flowgraph` |
   | `stateDiagram`, `stateDiagram-v2` | `d3.flowgraph` |
   | `sequenceDiagram` | `d3.sequence` |
   | `erDiagram` | `d3.erd` |
   | anything else (`gantt`, `classDiagram`, `pie`, ...) | skipped and listed |

2. **Check the result.** The script prints a summary, one line per skipped or failed diagram,
   and writes `diagrams/manifest.json`. The exit code is 1 when a supported diagram failed.

   | Manifest field | Meaning |
   |---|---|
   | `source`, `block`, `line` | file, diagram number in that file, first line inside the fence |
   | `kind`, `block_type` | Mermaid keyword; `flowgraph`, `sequence`, `erd` or `null` |
   | `status` | `ok`, `skipped` or `error` |
   | `output` | page path relative to the output folder (`ok` only) |
   | `counts` | elements in the page (nodes/edges, participants/messages, entities/relationships/columns) |
   | `error`, `error_line` | `file:line: message`, and the line in the source file |

3. **Fix failures.** d3blocks reads Mermaid strictly: a statement is understood, ignored
   (comments, `%%{init}%%`, `accTitle` / `accDescr`) or an error naming its line, so nothing is
   dropped silently. Each error message lists what is supported. Fix the diagram (or tell the
   user which Mermaid feature has no d3blocks equivalent), then run step 1 again. Do not delete
   statements just to make a diagram pass without saying so.

4. **Link the pages from the docs** (only if the user asks; the script never edits Markdown).
   The pages need no network access (scripts and styles are inline), so they work offline and
   under a strict Content-Security-Policy that allows inline scripts and styles. Either link
   (`[Open the interactive diagram](diagrams/docs/guide/1_flowchart.html)`) or embed
   (`<iframe src="diagrams/docs/guide/1_flowchart.html" style="width:100%;height:600px;border:0"></iframe>`).
   Keep the Mermaid block too if the docs must still render on GitHub.

## Captioned walkthrough for one diagram

The batch run has no captions. To add a step-by-step walkthrough to one diagram, render it
with the Python API and `steps`:

```python
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from convert_docs import find_blocks
from d3blocks import D3Blocks

line, text = find_blocks(Path("docs/guide.md").read_text())[0]  # diagram 1 of the file
steps = [
    {"title": "Validate", "caption": "Every order is checked first.",
     "highlight": {"nodes": ["check"], "edges": [("start", "check")]}},
]
D3Blocks().flowgraph(text, steps=steps, dark_mode="auto", filepath="diagrams/docs/guide/1_flowchart.html", showfig=False)
```

`highlight` takes `nodes` and `edges` for flowgraph (flowcharts and state diagrams) and erd,
and `messages` (indexes) and `participants` for sequence. For any block's parameters, run
`python -m pydoc d3blocks.D3Blocks.<block>`.
