# Treemap

Hierarchy as **nested rectangles**. Cell area reflects weight (or count).

## Input

DataFrame with either:

| Form | Columns |
|------|---------|
| Edge list | `source`, `target`, `weight` |
| Explicit levels | `level0`, `level1`, `level2`, … and `weight` |

Built-in samples: `d3.import_example('energy')`, `d3.import_example('animals')`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `value` | `'size'` | `'size'` (edge weight) or `'count'` (equal leaves) |
| `border` | `{'type': 'solid', 'color': '#FFFFFF', 'width': 0}` | Cell borders |
| `font` | `{'size': 10, 'type': 'sans-serif', 'position': 'absolute'}` | |
| `margin` | `{"top": 40, "right": 10, "bottom": 10, "left": 10}` | |
| `figsize` | `[1000, 600]` | |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.treemap
```

## Tree vs treemap

- **tree** — linked hierarchy diagram (nodes and edges).
- **treemap** — space-filling rectangles sized by value.

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.treemap(df, filepath='treemap.html')
```

### Size vs count mode

```python
d3.treemap(df, value='count', filepath='treemap_count.html')
```

### Tooltips via node properties

```python
d3 = D3Blocks(chart='treemap', frame=False)
df = d3.import_example('energy')
d3.set_node_properties(df)
d3.node_properties['Bio-conversion']['tooltip'] = 'Title: Bio conversion Operations'
d3.set_edge_properties(df)
d3.show(filepath='treemap_tooltip.html')
```

### HTML for embedding

```python
html = d3.treemap(
    df,
    value='size',
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/treemap_advanced.py`, `examples/streamlit_treemap.py`.  
Repo: `streamlit/treemap_streamlit_demo.py`.
