"""Run the skill's standalone examples against the installed d3blocks.

No browser is opened and no file is written outside pytest's tmp_path: d3blocks writes
relative filepaths to tempfile.gettempdir()/d3blocks/, which is redirected here.
"""

import runpy
import tempfile
import webbrowser
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parent / "examples"
STANDALONE = sorted(p for p in EXAMPLES.glob("*.py") if not p.name.startswith("streamlit_"))


@pytest.mark.parametrize("path", STANDALONE, ids=lambda p: p.name)
def test_example_runs(path, tmp_path, monkeypatch):
    monkeypatch.setattr(webbrowser, "open", lambda *args, **kwargs: True)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(path), run_name="__main__")
    assert list((tmp_path / "d3blocks").glob("*.html")), "the example wrote no HTML"
