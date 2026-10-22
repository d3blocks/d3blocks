# D3graph

Force-directed **network** graph (`source` / `target` / `weight`). Free layout (no focal rings — use `radialgraph` for that). Node/edge properties live on `d3.D3graph` after a call.

## Input

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node |
| `target` | yes | To node |
| `weight` | yes | Edge strength |

Samples: `import_example('energy')`, `'bigbang'`, `'stormofswords'`.

## Main parameters

| Parameter | Notes |
|-----------|--------|
| `scaler` | e.g. `'zscore'`, `'minmax'` |
| `collision` / `charge` | Force layout |
| `size` | Node size default |
| `show_side_panel` / `show_top_panel` | UI chrome |
| `dark_mode` / `color_background` | theme |
| `return_html` / `filepath` / `showfig` | standard |

Exact signature: `python -m pydoc d3blocks.D3Blocks.d3graph`.

## vs elasticgraph / radialgraph

- **d3graph** — free force layout  
- **elasticgraph** — clustered groups (Louvain hulls) on top of the same edge idea  
- **radialgraph** — rings by hop-distance from a focus  

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.d3graph(df, filepath='d3graph.html')
```

### Scaler and node edits

```python
d3.d3graph(df, scaler='minmax')
d3.D3graph.set_node_properties(color=None)
d3.D3graph.node_properties['Solar']['size'] = 30
d3.D3graph.show()
```

### HTML for embedding

```python
html = d3.d3graph(
    df,
    showfig=False,
    return_html=True,
    filepath=None,
    dark_mode=False,
    color_background='streamlit',
)
```

## Full runnable examples

`examples/d3graph_advanced.py`, `examples/streamlit_d3graph.py`.  
Repo: `streamlit/d3graph_streamlit_demo.py`.
