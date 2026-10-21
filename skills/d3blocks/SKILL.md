---
name: d3blocks
description: Use this skill when users want to create interactive data visualizations using D3Blocks from a pandas DataFrame. Guides chart selection, parameters, runnable Python examples, and Streamlit embedding. Trigger when users mention data and want scatter plots, chord diagrams, flowgraphs, networks, heatmaps, or other D3Blocks visualizations, or want to embed a chart in Streamlit.
metadata:
  Github: D3Blocks
  version: "1.0.1"
---


# D3Blocks Visualizer

D3Blocks is a Python library for interactive D3.js charts from Python. Output is self-contained HTML.

## When to use

- Interactive visualization from Python data
- Relationships, networks, flows, scatter exploration
- Export or embed HTML (including Streamlit / notebooks)
- Customize an existing D3Blocks chart

## Choosing a visualization

| Goal | Prefer |
|------|--------|
| Two continuous variables, brushing, multi-coord transitions | `scatter` |
| Circular flows between categories (source/target/weight) | `chord` |
| Process / architecture diagram, Mermaid flowchart or state diagram | `flowgraph` |
| Networks / relationships | `d3graph` |
| Hierarchical networks | `radialgraph` |
| Auto-clustered networks | `elasticgraph` |
| Two categorical dimensions of values | `heatmap` |
| Hierarchical nested circles | `circlepacking` |
| Hierarchical sized rectangles | `treemap` / `tree` |
| Image comparison | `imageslider` |
| Geographic | `maps` |
| Row–column matrix | `matrix` |
| Animated bubbles over time | `movingbubbles` |
| Particles | `particles` |
| Stage-to-stage flows | `sankey` |
| Variables over time | `timeseries` |
| Mermaid `sequenceDiagram` | `sequence` |
| Mermaid `erDiagram` / schema | `erd` |
| Distributions across groups | `violin` |

## Guidance steps

1. Understand the data (columns, types, what each means).
2. Pick a chart from the table above.
3. For a chart's parameters run `python -m pydoc d3blocks.D3Blocks.<chart>` (e.g. `d3blocks.D3Blocks.scatter`); it prints the signature and docstring of the installed version. Open `references/<chart>.md` for input shape and gotchas, and `examples/` for full runnable code.
4. Give a **runnable** sample with the correct call signature (do not invent APIs).
5. For Streamlit, use `examples/streamlit_*.py` and `references/streamlit.md` — do not invent a different embed pattern.

## Common parameters (most charts)

- `title`, `filepath`, `figsize`, `showfig`, `overwrite`, `notebook`, `save_button`
- `show_side_panel`, `show_top_panel` (independent; bool)
- `dark_mode`: `True` | `False` | `'auto'` (where supported)
- `color_background`: `[dark_hex, light_hex]`, a named theme, or `'streamlit'`
- `return_html`: return HTML string instead of only writing a file
- `reset_properties`: reset node/edge properties each run

## API reminders

- **Scatter** takes `x=` and `y=` arrays (optional `x1`/`y1`…). Never `d3.scatter(df)`.
- **Chord** needs DataFrame columns `source`, `target`, `weight`.
- **Flowgraph** accepts an edge-list DataFrame or a Mermaid string/file; use `D3Blocks(frame=False)` when editing `node_properties` as a dict.
- **Streamlit**: `showfig=False`, `return_html=True`, `color_background='streamlit'`, embed with `st.iframe`. Prefer `show_side_panel=False` when Streamlit owns the controls.

## Where the code lives

| Need | Location |
|------|----------|
| Scatter (multi-coord, encodings, tooltips) | `examples/scatter_advanced.py` |
| Chord (ordering, property edits, highlights) | `examples/chord_advanced.py` |
| Flowgraph (shapes, groups, Mermaid, ELK, state) | `examples/flowgraph_advanced.py` |
| Streamlit + scatter | `examples/streamlit_scatter.py` |
| Streamlit + chord | `examples/streamlit_chord.py` |
| Streamlit + flowgraph | `examples/streamlit_flowgraph.py` |
| Parameters (any chart) | `python -m pydoc d3blocks.D3Blocks.<chart>` |
| Input shape and gotchas | `references/scatter.md`, `chord.md`, `flowgraph.md` |
| Streamlit rules | `references/streamlit.md` |

Repo demos (optional): `streamlit/scatter_streamlit_demo.py`, `streamlit/chord_streamlit_demo.py`.

## Installation

Requires d3blocks 2.3.0 or later (`sequence`, `erd` and `dark_mode='auto'` are new in 2.3.0).

```bash
pip install -U d3blocks
# optional
pip install streamlit
```
