# Radialgraph

Force-directed network laid out in **concentric rings by hop-distance** from a focal node (Obsidian-style local graph). Same `source` / `target` / `weight` input as `d3graph`; appearance (color, size, opacity, edge width) is computed like `d3graph` — only the layout differs.

## Input

DataFrame with:

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node |
| `target` | yes | To node |
| `weight` | yes | Link strength |

Built-in sample: `d3.import_example('energy')`.

Many-to-many edges; no hierarchy or single-root assumption.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `center` | `None` | Focal node; `None` = highest-degree node |
| `ring_spacing` | `70` | Pixels between depth rings |
| `auto_ring_spacing` | `True` | Derive spacing from ring population |
| `radial_strength` | `0.8` | How tightly nodes snap to their ring (0–1) |
| `charge` | `-120` | Node repulsion (same idea as d3graph) |
| `collision` / `link_distance` / `link_strength` | force tunables | |
| `color` | `'cluster'` | Node color: `'cluster'`, `'degree'`, … |
| `size` | `'degree'` | Node size encoding |
| `opacity` | `'degree'` | Node opacity encoding |
| `cmap` / `scaler` / `minmax` | appearance scaling | |
| `edge_color` / `edge_opacity` / `edge_minmax` | link appearance | |
| `min_weight` | `1.0` | Drop weaker edges |
| `significance_test` | `None` | e.g. `'pagerank'` (Python-side via d3graph) |
| `expand_all_on_load` | `False` | Expand all rings on first paint |
| `show_side_panel` / `show_top_panel` / `show_bottom_panel` | `True` | UI chrome (bottom panel is node-focused) |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` / `figsize` | standard | |

For the live signature of the installed package:

```bash
python -m pydoc d3blocks.D3Blocks.radialgraph
```

## When to prefer radialgraph vs d3graph

- **radialgraph** — explore a network *around a focus* (rings by hop distance).
- **d3graph** — free force layout, no focal center.
- Same edge list works for both; appearance settings are aligned on purpose.

## Examples

### Basic (auto center = highest degree)

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.radialgraph(df, filepath='radialgraph.html')
```

### Explicit center

```python
d3.radialgraph(df, center='Solar', filepath='radialgraph_solar.html')
```

### Significance test + layout knobs

```python
d3.radialgraph(
    df,
    center='Nuclear',
    significance_test='pagerank',
    radial_strength=0.9,
    ring_spacing=80,
    charge=-150,
    color='cluster',
    size='degree',
    show_bottom_panel=True,
    filepath='radialgraph_pagerank.html',
)
```

### HTML for embedding

```python
html = d3.radialgraph(
    df,
    center=None,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

In this skill: `examples/radialgraph_advanced.py` and `examples/streamlit_radialgraph.py`.
Repo demo: `streamlit/radialgraph_streamlit_demo.py`.
