"""Run scaffold_chart.py into a temporary copy of the d3blocks package.

Fails when the scaffold no longer produces an importable block, or when its output leaks
names of the existing charts (`--check`).
"""

import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent
REPO = SKILL.parents[1]
SCAFFOLD = SKILL / "scripts" / "scaffold_chart.py"


def test_scaffold_creates_an_importable_block_without_leaks(tmp_path):
    pkg = tmp_path / "d3blocks"
    shutil.copytree(
        REPO / "d3blocks", pkg, ignore=shutil.ignore_patterns("tests", "__pycache__")
    )
    tests_dir, demo_dir = tmp_path / "tests", tmp_path / "streamlit"
    tests_dir.mkdir()
    demo_dir.mkdir()
    args = [
        sys.executable,
        str(SCAFFOLD),
        "--name",
        "zzchart",
        "--prefix",
        "zz",
        "--pkg-dir",
        str(pkg),
        "--tests-dir",
        str(tests_dir),
        "--demo-dir",
        str(demo_dir),
    ]

    made = subprocess.run(args, capture_output=True, text=True)
    assert made.returncode == 0, made.stdout + made.stderr

    check = subprocess.run(args + ["--check"], capture_output=True, text=True)
    assert check.returncode == 0, check.stdout + check.stderr

    # Import the new block from the copy (the working directory comes first on sys.path).
    imported = subprocess.run(
        [
            sys.executable,
            "-c",
            "from d3blocks.zzchart import Zzchart; print(Zzchart.__file__)",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert imported.returncode == 0, imported.stderr
    assert str(pkg) in imported.stdout
