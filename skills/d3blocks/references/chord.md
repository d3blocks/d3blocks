# Chord

Circular layout for flows between entities. Outer arcs are nodes; ribbons are weighted links.

## Input

DataFrame with:

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node |
| `target` | yes | To node |
| `weight` | yes | Link strength (arc thickness) |
| `color` | no | Per-link color override |
| `opacity` | no | Per-link opacity override |

Built-in sample: `d3.import_example('energy')`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `color` | `'source'` | `'source'`, `'target'`, `'source-target'`, hex, or list of hex |
| `opacity` | `'source'` | `'source'`, `'target'`, float, or list |
| `ordering` | `'ascending'` | `'ascending'`, `'descending'`, `''`, or explicit label list |
| `fontsize` | `10` | Label font size |
| `arrowhead` | `10` | Arrow size |
| `cmap` | `'tab20'` | Colormap for nodes/links |
| `margin` | `150` | Space for labels (increase for long names) |
| `text_offset` | `5` | Label distance from arc |
| `figsize` | `[900, 900]` | Browser size |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` | `True` | `True` / `False` / `'auto'` where supported |
| `color_background` | `None` | e.g. `'streamlit'` or `[dark, light]` |
| `return_html` | `False` | Return HTML string |
| `filepath` | `'chord.html'` | `None` to skip file write when returning HTML |

## Examples

### Basic (energy flows)

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.chord(df, filepath='chord.html')
```

### Large margins for long labels

```python
d3.chord(
    df,
    filepath='chord_large_margins.html',
    figsize=[1200, 1200],
    margin=300,
    text_offset=50,
)
```

### Edit node and edge properties, then redraw

```python
from d3blocks import D3Blocks

d3 = D3Blocks(chart='Chord', frame=False)
df = d3.import_example('energy')

d3.set_node_properties(df, opacity=0.2, cmap='tab20')
d3.set_edge_properties(df, color='source', opacity='source')
d3.show()

# Highlight Nuclear
d3.node_properties.get('Nuclear')['color'] = '#ff0000'
d3.node_properties.get('Nuclear')['opacity'] = 1
d3.show()

# Highlight one edge
mask = (
    (d3.edge_properties['source'] == 'Nuclear')
    & (d3.edge_properties['target'] == 'Thermal generation')
)
d3.edge_properties.loc[mask, 'color'] = '#ff0000'
d3.edge_properties.loc[mask, 'opacity'] = 0.8
d3.edge_properties.loc[mask, 'weight'] = 1000
d3.show()
```

### Custom ordering

```python
# Fixed label order (list) or sort
d3.chord(df, ordering='descending')
# d3.chord(df, ordering=['LabelA', 'LabelB', ...])
```

### Return HTML / Streamlit-friendly

```python
html = d3.chord(
    df,
    show_side_panel=True,
    show_top_panel=True,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

See `references/streamlit.md` and repo file `streamlit/chord_streamlit_demo.py`.

## Full runnable examples

In this skill: `examples/chord_advanced.py and examples/streamlit_chord.py`.
