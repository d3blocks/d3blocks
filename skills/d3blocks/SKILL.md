---
name: d3blocks
description: Use this skill whenever users want interactive D3Blocks charts from Python data (pandas DataFrame, arrays, Mermaid, images, or text). Always clarify data source and columns first, suggest suitable chart types, and let the user choose before writing code. Covers chart selection, call signatures, runnable examples under examples/, and Streamlit embedding. Trigger for D3Blocks or d3blocks requests, and for goals that match documented charts—scatter, violin, chord, sankey, d3graph, elasticgraph, radialgraph, heatmap, matrix, tree, treemap, circlepacking, maps, timeseries, movingbubbles, flowgraph, sequence, erd, imageslider, particles—or embedding any of these in Streamlit/notebooks. Also trigger for edge lists (source/target/weight), hierarchies, geo lon/lat, before/after images, sequence/ER diagrams, or “interactive HTML chart from my CSV”.
metadata:
  Github: D3Blocks
  version: "1.0.0"
---


# D3Blocks Visualizer

D3Blocks is a Python library for interactive D3.js charts from Python. Output is self-contained HTML.

> `d3blocks` 2.3.0 or later is needed. Do not run `pip install` first; write the code and import it directly. Only if the import fails, or `d3blocks.__version__` is older than 2.3.0: install it (until 2.3.0 is on PyPI: `pip install git+https://github.com/d3blocks/d3blocks`).

## When to use

- Interactive D3.js charts from Python (output is self-contained HTML)
- Exploratory plots (scatter, violin), flows (chord, sankey), networks (d3graph, elasticgraph, radialgraph)
- Hierarchies (tree, treemap, circlepacking), matrices (heatmap, matrix), maps, timeseries / movingbubbles
- Diagrams from Mermaid or tables (flowgraph, sequence, erd)
- Imageslider, particles, or Streamlit / notebook embeds of any of the above
- Customizing node/edge properties on an existing D3Blocks chart

For the full set of charts this skill documents, list `references/*.md` and `examples/*_advanced.py`. Prefer the chooser table below, then open `references/<chart>.md` and the matching example.

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

To convert *all* the Mermaid diagrams in a repository's docs at once, use the
`d3blocks-diagrams` skill instead.

## Guidance steps (ask before you build)

Do **not** jump straight to code. Clarify data and intent first, propose chart options, then implement only after the user chooses.

### 1. Data source

Ask where the data is (or will come from), for example:

- Path to a file (`csv`, `tsv`, `xlsx`, parquet, …)
- Already in memory (DataFrame name / notebook cell)
- Built-in sample via `d3.import_example(...)` if they have no file yet
- Database / API only if they say so

If a path is given, load a small preview (columns, dtypes, a few rows) before recommending a chart. If the file is missing or unreadable, say so and ask again.

### 2. Relevant columns

Ask which columns matter for the question they care about. Map answers to roles the charts need, e.g.:

| Role | Typical columns | Charts that need them |
|------|-----------------|------------------------|
| Continuous x / y | numeric | `scatter`, `timeseries`, `violin` |
| Categories / groups | string / category | `scatter` color, `heatmap`, `violin` |
| Flow from → to | source, target | `chord`, `sankey`, `d3graph`, `radialgraph`, `flowgraph` |
| Link strength | weight / value | `chord`, `sankey`, `d3graph`, `radialgraph` |
| Network around a focus | source, target, weight (+ optional center) | `radialgraph` (rings by hop); `d3graph` for free layout |
| Hierarchy / parent | id, parent, value | `tree`, `treemap`, `circlepacking` |
| Time | datetime / period | `timeseries`, `movingbubbles` |
| Entity × state over time | datetime, sample_id, state | `movingbubbles` |
| Matrix / adjacency | index × columns of values | `heatmap` |
| Geo points | lon, lat | `maps` |
| Country choropleth | country name list | `maps` (`country_names`) |
| Process / diagram text | Mermaid or edge list | `flowgraph`, `sequence`, `erd` |

If they are unsure, propose a short column mapping from the preview (“`A` → source, `B` → target, `C` → weight”) and ask them to confirm or correct it.

### 3. Chart suggestion (user decides)

Using their goal **and** the column roles, suggest **2–3** suitable charts from the table above. For each option, one sentence on why it fits and what it needs. Example shape:

- **Recommended:** `chord` — you have source/target/weight flows between categories.
- **Also fits:** `sankey` — same edge list, left-to-right stages instead of a circle.
- **If you care about network structure more than volume:** `d3graph` (free layout) or `radialgraph` (rings around a focus node).

State a preference when one is clearly best, but **always let the user pick**. Do not implement until they confirm the chart (and column mapping). If they name a chart that the data cannot support, explain the mismatch and offer alternatives.

### 4. Implement

Only after data source, columns, and chart type are agreed:

1. For parameters, run `python -m pydoc d3blocks.D3Blocks.<chart>` (installed version). Open `references/<chart>.md` for input shape/gotchas and `examples/` for full runnable code.
2. Write a **runnable** sample with the correct call signature (do not invent APIs).
3. For Streamlit, use `examples/streamlit_*.py` and `references/streamlit.md` — do not invent a different embed pattern.

Skip steps 1–3 only when the user already supplied path, columns, and an explicit chart type in the same message.

## Common parameters (most charts)

- `title`, `filepath`, `figsize`, `showfig`, `overwrite`, `notebook`, `save_button`
- `show_side_panel`, `show_top_panel` (independent; bool)
- `dark_mode`: `True` | `False` | `'auto'` (where supported)
- `color_background`: `[dark_hex, light_hex]`, a named theme, or `'streamlit'`
- `return_html`: return HTML string instead of only writing a file
- `reset_properties`: reset node/edge properties each run

## API reminders

- **Scatter** / **violin** take coordinate arrays (`x=` / `y=`), not a lone DataFrame. Never `d3.scatter(df)` or `d3.violin(df)`.
- **Chord** / **sankey** / **radialgraph** / **d3graph** / **elasticgraph** / **tree** / **treemap** / **circlepacking** share an edge list: `source`, `target`, `weight` (treemap/circlepacking also accept `level0`/`level1`/…).
- **D3graph**: free force layout; edit via `d3.D3graph.node_properties` after a call.
- **Elasticgraph**: clustered groups (Louvain hulls); edit via `d3.Elasticgraph.D3graph`.
- **Circlepacking**: nested circles (`size='sum'|'constant'`, `zoom='click'|'mouseover'`).
- **Matrix**: DataFrame as a matrix (index/columns labels); simpler alternative to `heatmap`.
- **Heatmap**: matrix or network samples; optional `cluster_params` / `color`.
- **Maps**: markers need `lon`/`lat` (e.g. `import_example('surfspots')`); or `country_names=[...]` for choropleth without markers.
- **Timeseries**: datetime column + numeric series; set `datetime=` and `dt_format=`. Continuous series — not `movingbubbles`.
- **Particles**: single text string → interactive particles.
- **Imageslider**: `img_before`, `img_after` (or `import_example('southern_nebula_internet')`).
- **Sequence**: messages (`source`/`target`/`label`/`style`) or Mermaid `sequenceDiagram`. Confirm `D3Blocks.sequence` with pydoc.
- **ERD**: relationships + cardinalities or Mermaid `erDiagram`. Confirm `D3Blocks.erd` with pydoc.
- **Sankey**: left-to-right stages; tune `node=` / `link=` dicts. **Chord**: circular category flows.
- **Tree**: hierarchy diagram; **treemap**: nested rectangles (`value='size'|'count'`).
- **Radialgraph**: optional `center` (node name) or auto highest-degree; prefer over `d3graph` when exploring *around a focus*.
- **Movingbubbles** needs `datetime`, `sample_id`, `state` (column names configurable); use `import_example('random_time', ...)` for demos.
- **Flowgraph** accepts an edge-list DataFrame or a Mermaid string/file; use `D3Blocks(frame=False)` when editing `node_properties` as a dict.
- **Streamlit**: `showfig=False`, `return_html=True`, `color_background='streamlit'`, embed with `st.iframe`. Prefer `show_side_panel=False` when Streamlit owns the controls.

## Where the code lives

Do not rely on a fixed chart list here — discover what this skill covers by listing the folders.

| Need | Location |
|------|----------|
| Charts with deeper notes | `references/<chart>.md` (any `.md` except `streamlit.md`) |
| Runnable standalone example | `examples/<chart>_advanced.py` when present |
| Streamlit app for a chart | `examples/streamlit_<chart>.py` when present |
| Streamlit embed rules | `references/streamlit.md` |
| Parameters (any chart) | `python -m pydoc d3blocks.D3Blocks.<chart>` |
| Repo Streamlit demos (optional) | `streamlit/<chart>_streamlit_demo.py` when present in the project |

If `references/<chart>.md` is missing, still use pydoc + the chooser table above; do not invent APIs.

## Dependencies

`d3blocks` 2.3.0 or later (pip; brings pandas, numpy and jinja2. Install only if the import fails or the version is older; until 2.3.0 is on PyPI, install from `git+https://github.com/d3blocks/d3blocks`) · `streamlit` (pip, only for the `examples/streamlit_*.py` apps; install only if the import fails)
