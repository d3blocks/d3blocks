# Sankey

Stage-to-stage **flow** diagram. Nodes are vertical rectangles; link width is proportional to `weight`. Best for many-to-many paths through ordered stages (e.g. energy mixes, website funnels).

## Input

DataFrame with:

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node / stage |
| `target` | yes | To node / stage |
| `weight` | yes | Flow magnitude (link thickness) |

Built-in samples: `d3.import_example('energy')`, `d3.import_example('stormofswords')`.

Same edge-list shape as `chord` / `d3graph` / `radialgraph`. Prefer **sankey** for left-to-right stages; **chord** for circular category flows.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `node` | `{"align": "justify", "width": 15, "padding": 15, "color": "currentColor"}` | `align`: `left` / `right` / `justify` / `center` |
| `link` | `{"color": "source-target", "stroke_opacity": 0.5, "color_static": "#d3d3d3"}` | `color`: `source` / `target` / `source-target` |
| `color` | `None` | Dict of node name → hex, e.g. `{'Nuclear': '#FF0000'}` |
| `fontsize` | `10` | Int for all nodes, or dict per node name |
| `margin` | `{"top": 5, "right": 1, "bottom": 5, "left": 1}` | Pixels |
| `figsize` | `[1024, 768]` | Browser size |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

Live signature:

```bash
python -m pydoc d3blocks.D3Blocks.sankey
```

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.sankey(df, filepath='sankey.html')
```

### Link and node layout

```python
d3.sankey(
    df,
    link={'color': 'source', 'stroke_opacity': 0.6, 'color_static': '#d3d3d3'},
    node={'align': 'left', 'width': 20, 'padding': 12, 'color': 'currentColor'},
    fontsize=12,
    figsize=[1100, 800],
    filepath='sankey_left.html',
)
```

### Custom node colours + editable properties

```python
from d3blocks import D3Blocks

d3 = D3Blocks(chart='Sankey', frame=True)
df = d3.import_example('energy')

d3.set_node_properties(
    df,
    color={
        'Nuclear': '#FF0000',
        'Wind': '#FF0000',
        'Electricity grid': '#7FFFD4',
        'Bio-conversion': '#000000',
        'Industry': '#000000',
    },
)
d3.set_edge_properties(df, color='target', opacity='target')
d3.show(filepath='sankey_custom.html')
```

### One-shot colour dict

```python
d3.sankey(
    df,
    color={'Nuclear': '#FF0000', 'Wind': '#000000', 'Electricity grid': '#FF0000'},
    filepath='sankey_highlight.html',
)
```

### HTML for embedding

```python
html = d3.sankey(
    df,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

In this skill: `examples/sankey_advanced.py` and `examples/streamlit_sankey.py`.  
Repo demo: `streamlit/sankey_streamlit_demo.py`.
