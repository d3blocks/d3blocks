# D3Blocks Visualizer Skill

Helps an AI coding agent create interactive D3Blocks charts from Python data: clarifying
the data source and columns first, suggesting charts for the user to choose, then writing
runnable code and Streamlit embeds.

Start from [`SKILL.md`](SKILL.md). For a chosen chart, open `references/<chart>.md` (input
shape and gotchas) and the matching files under `examples/` (`<chart>_advanced.py`,
`streamlit_<chart>.py` when present). Live method signatures come from the installed
package: `python -m pydoc d3blocks.D3Blocks.<chart>`.

## Install

```bash
npx skills add erdogant/d3blocks --skill d3blocks
pip install git+https://github.com/d3blocks/d3blocks  # d3blocks 2.3.0 or later; until it is on PyPI
```

## Maintain

- Chart parameters come from the installed package (`python -m pydoc d3blocks.D3Blocks.<chart>`),
  so they are not copied into this skill.
- `pytest skills/d3blocks` checks the skill's structure and runs every standalone example in
  `examples/` against the installed d3blocks; CI runs it too.
