# Elasticgraph

Force-directed network with **clustered groups** (Louvain modularity). Same edge list as `d3graph`; groups form elastic hulls. Internals reuse d3graph properties via `d3.Elasticgraph.D3graph`.

## Input

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node |
| `target` | yes | To node |
| `weight` | yes | Edge strength |

Samples: `energy`, `stormofswords`, `bigbang`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `scaler` | `'zscore'` | Edge scaling |
| `group` | `'cluster'` | Grouping mode |
| `collision` | `0.5` | |
| `charge` | `500` | (stored as negative force) |
| `size` | `4` | Node size |
| `hull_offset` | `15` | Cluster hull padding |
| `single_click_expand` | `False` | |
| `sticky` | `True` | |
| `label_zoom_threshold` | `0.4` | |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.elasticgraph
```

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.elasticgraph(df, filepath='Elasticgraph.html')
```

### Edit via Elasticgraph.D3graph then show

```python
d3.elasticgraph(df, showfig=False)
d3.Elasticgraph.D3graph.node_properties['Wind']['size'] = 20
d3.Elasticgraph.D3graph.edge_properties[('Wind', 'Electricity_grid')]['label'] = 'Test'
d3.Elasticgraph.show()
# Underlying force graph only:
d3.Elasticgraph.D3graph.show()
```

### HTML for embedding

```python
html = d3.elasticgraph(
    df,
    showfig=False,
    return_html=True,
    dark_mode=False,
    color_background='streamlit',
)
```

## Full runnable examples

`examples/elasticgraph_advanced.py`, `examples/streamlit_elasticgraph.py`.  
Repo: `streamlit/elasticgraph_streamlit_demo.py`.
