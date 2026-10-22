"""Run the skill's standalone examples against the installed d3blocks.

No browser is opened and no file is written outside pytest's tmp_path: chart code may use
different subdirectories under tempfile.gettempdir(), which is redirected here.
"""

import runpy
import tempfile
import webbrowser
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parent / "examples"
STANDALONE = sorted(
    p for p in EXAMPLES.glob("*.py") if not p.name.startswith("streamlit_")
)

# sequence/erd need methods that some package builds omit
OPTIONAL_METHODS = {
    "sequence_advanced.py": "sequence",
    "erd_advanced.py": "erd",
}


@pytest.mark.parametrize("path", STANDALONE, ids=lambda p: p.name)
def test_example_runs(path, tmp_path, monkeypatch):
    method = OPTIONAL_METHODS.get(path.name)
    if method:
        from d3blocks import D3Blocks

        if not hasattr(D3Blocks(), method):
            pytest.skip(f"D3Blocks has no .{method}()")
    monkeypatch.setattr(webbrowser, "open", lambda *args, **kwargs: True)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(path), run_name="__main__")
    assert list(tmp_path.rglob("*.html")), "the example wrote no HTML"
