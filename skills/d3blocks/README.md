# D3Blocks Visualizer Skill

Helps an AI coding agent create interactive D3Blocks charts from Python data: picking the
chart, writing runnable code, and embedding it in Streamlit. Everything the agent reads is in
[`SKILL.md`](SKILL.md), which links to `references/` and `examples/`.

## Install

```bash
npx skills add erdogant/d3blocks --skill d3blocks
pip install d3blocks
```

## Maintain

- Chart parameters come from the installed package (`python -m pydoc d3blocks.D3Blocks.<chart>`),
  so they are not copied into this skill.
- `pytest skills/d3blocks` checks the skill's structure and runs every standalone example in
  `examples/` against the installed d3blocks; CI runs it too.
