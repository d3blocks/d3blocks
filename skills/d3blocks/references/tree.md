# Tree

Hierarchical tree layout from an edge list. Nodes expand/collapse by hierarchy level.

## Input

DataFrame with:

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | Parent / from |
| `target` | yes | Child / to |
| `weight` | yes | Link weight (used in properties) |

Built-in sample: `d3.import_example('energy')`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `hierarchy` | `[1..8]` | Which depth levels are expanded |
| `link_length` | `180` | Horizontal distance between levels (px) |
| `margin` | `{"top": 20, "right": 80, "bottom": 20, "left": 60}` | |
| `font` | `{'size': 10}` | |
| `figsize` | `[960, 700]` | |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.tree
```

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.tree(df, filepath='tree.html')
```

### Edit node properties then show

```python
d3 = D3Blocks(verbose='info', chart='tree', frame=False)
df = d3.import_example('energy')
d3.set_node_properties(df)

d3.node_properties.get('Bio-conversion')['size'] = 30
d3.node_properties.get('Bio-conversion')['color'] = '#000000'
d3.node_properties.get('Losses')['color'] = '#FF0000'

d3.set_edge_properties(df)
d3.show(hierarchy=[1, 2, 3, 4, 5, 6, 7, 8], filepath='tree_styled.html')
```

### HTML for embedding

```python
html = d3.tree(
    df,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/tree_advanced.py`, `examples/streamlit_tree.py`.
