# D3Blocks Docs Diagrams Skill

Helps an AI coding agent convert all the Mermaid diagrams in a repository's docs into
standalone, interactive D3Blocks pages, and report the ones that fail with their file and line.
Everything the agent reads is in [`SKILL.md`](SKILL.md); the work is done by
`scripts/convert_docs.py`.

## Install

```bash
npx skills add erdogant/d3blocks --skill d3blocks-docs-diagrams
pip install git+https://github.com/d3blocks/d3blocks  # d3blocks 2.3.0 or later; until it is on PyPI
```

## Maintain

- `pytest skills/d3blocks-docs-diagrams` runs the script on a small docs tree (every supported
  diagram type, a skipped kind and a failing diagram); CI runs it too.
- The script finds blocks with the same pattern as `d3blocks.flowgraph.Flowgraph.read_mermaid`;
  a test keeps the two in step.
