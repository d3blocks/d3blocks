"""Tests for scripts/convert_docs.py against a small docs tree."""

import json
import re
import subprocess
import sys
from pathlib import Path

from d3blocks.flowgraph import Flowgraph

SCRIPT = Path(__file__).resolve().parent / "scripts" / "convert_docs.py"

GUIDE = """# Guide

Intro text.

```mermaid
flowchart LR
  A[Start] --> B{Ok?}
```

```mermaid
stateDiagram-v2
  [*] --> idle
  idle --> busy : start
```

```mermaid
sequenceDiagram
  A->>B: request
  B-->>A: response
```

```mermaid
erDiagram
  customers ||--o{ orders : places
```

```mermaid
gantt
  title Plan
```

```mermaid
flowchart LR
  A --> B
  click A callback
```
"""
ALL_KINDS = Flowgraph.MERMAID_KINDS + ("sequenceDiagram", "erDiagram")


def _tree(tmp_path, broken=True):
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    text = GUIDE if broken else GUIDE.replace("  click A callback\n", "")
    (docs / "guide.md").write_text(text, encoding="utf-8")
    (docs / "sub" / "flow.mmd").write_text("graph TD\n  X --> Y\n", encoding="utf-8")
    skipped = docs / "node_modules"
    skipped.mkdir()
    (skipped / "vendor.md").write_text(
        "```mermaid\ngraph LR\n  P --> Q\n```\n", encoding="utf-8"
    )
    return docs


def _run(tmp_path, *paths):
    out = tmp_path / "out"
    cmd = [sys.executable, str(SCRIPT), *map(str, paths), "--out", str(out)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    return done, out, manifest


def test_converts_every_supported_block(tmp_path):
    docs = _tree(tmp_path)
    done, out, manifest = _run(tmp_path, docs)
    rows = {(r["source"], r["block"]): r for r in manifest}

    assert {r["source"] for r in manifest} == {
        "docs/guide.md",
        "docs/sub/flow.mmd",
    }  # node_modules skipped
    expected = {
        1: ("flowchart", "flowgraph", "ok"),
        2: ("stateDiagram-v2", "flowgraph", "ok"),
        3: ("sequenceDiagram", "sequence", "ok"),
        4: ("erDiagram", "erd", "ok"),
        5: ("gantt", None, "skipped"),
        6: ("flowchart", "flowgraph", "error"),
    }
    for block, (kind, block_type, status) in expected.items():
        row = rows[("docs/guide.md", block)]
        assert (row["kind"], row["block_type"], row["status"]) == (
            kind,
            block_type,
            status,
        ), row
    assert rows[("docs/sub/flow.mmd", 1)]["status"] == "ok"

    # Start lines are lines in the Markdown file (the first line inside the fence).
    lines = GUIDE.splitlines()
    assert lines[rows[("docs/guide.md", 1)]["line"] - 1] == "flowchart LR"
    assert lines[rows[("docs/guide.md", 3)]["line"] - 1] == "sequenceDiagram"

    for row in manifest:
        if row["status"] != "ok":
            assert row["output"] is None
            continue
        page = out / row["output"]
        assert page.is_file(), row
        html = page.read_text(encoding="utf-8")
        assert not re.search(r"<(script|link)[^>]+(src|href)=[\"']https?:", html)
    assert rows[("docs/guide.md", 1)]["output"] == "docs/guide/1_flowchart.html"
    assert rows[("docs/guide.md", 3)]["counts"] == {
        "participants": 2,
        "messages": 2,
        "regions": 0,
    }
    assert rows[("docs/guide.md", 4)]["counts"]["entities"] == 2


def test_error_names_the_markdown_line_and_fails_the_run(tmp_path):
    docs = _tree(tmp_path)
    done, out, manifest = _run(tmp_path, docs)
    assert done.returncode == 1
    error = next(r for r in manifest if r["status"] == "error")
    click_line = GUIDE.splitlines().index("  click A callback") + 1
    assert error["error_line"] == click_line
    assert error["error"].startswith("docs/guide.md:%d: " % click_line)
    assert "click A callback" in error["error"]
    assert "docs/guide.md:%d" % click_line in done.stdout


def test_skipped_kinds_do_not_fail_the_run(tmp_path):
    docs = _tree(tmp_path, broken=False)
    done, out, manifest = _run(tmp_path, docs)
    assert done.returncode == 0, done.stdout + done.stderr
    assert [r["status"] for r in manifest].count("skipped") == 1


def test_first_supported_block_matches_read_mermaid(tmp_path):
    # The script carries a copy of read_mermaid's block regex; both must find the same block.
    docs = _tree(tmp_path)
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import convert_docs
    finally:
        sys.path.pop(0)
    blocks = convert_docs.find_blocks((docs / "guide.md").read_text(encoding="utf-8"))
    first = next(text for _, text in blocks if convert_docs.block_type(text))
    assert first == Flowgraph.read_mermaid(docs / "guide.md", kinds=ALL_KINDS)


def test_rejects_missing_paths_and_other_files(tmp_path):
    other = tmp_path / "notes.txt"
    other.write_text("graph LR\n  A --> B\n", encoding="utf-8")
    for path, message in (
        (tmp_path / "nope", "does not exist"),
        (other, "not a Markdown"),
    ):
        cmd = [sys.executable, str(SCRIPT), str(path), "--out", str(tmp_path / "out")]
        done = subprocess.run(cmd, capture_output=True, text=True)
        assert done.returncode == 2 and message in done.stderr, done.stderr
