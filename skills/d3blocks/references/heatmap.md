# Heatmap

Interactive **adjacency heatmap** with optional clustering. Index and column names label rows/columns. Symmetric matrices work best for network-style data.

## Input

`pd.DataFrame` used as a matrix:

- **Index** → row labels  
- **Columns** → column labels  
- **Values** → cell intensities  

Or an edge list that the chart converts (examples use `stormofswords`, `energy`, `bigbang` via `import_example`).

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `scaler` | `'zscore'` | `'zscore'`, `'minmax'`, or `None` |
| `color` | `'cluster'` | `'cluster'`, `'label'`, list of class ids, or list of hex |
| `cmap` | `'Set2'` | |
| `stroke` | `'red'` | Hover/stroke accent |
| `fontsize` / `fontsize_mouseover` | `10` / `18` | |
| `cluster_params` | agglomerative + silhouette, etc. | Tuning for clustering |
| `description` | `None` | Optional HTML description |
| `figsize` | `[720, 720]` | |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.heatmap
```

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('stormofswords')
d3.heatmap(df, filepath='heatmap.html')
```

### Custom cluster params

```python
d3.heatmap(
    df,
    cluster_params={
        'evaluate': 'dbindex',
        'metric': 'hamming',
        'linkage': 'complete',
        'normalize': False,
        'min_clust': 3,
        'max_clust': 15,
    },
)
```

### Colour by label or hex list

```python
df = d3.import_example('bigbang')
d3.heatmap(df, color=[1, 1, 1, 2, 2, 2, 3])
d3.heatmap(df, color=['#FFF000', '#FFF000', '#FFF000', '#000FFF', '#000FFF', '#000FFF', '#000FFF'])
```

### HTML for embedding

```python
html = d3.heatmap(
    df,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/heatmap_advanced.py`, `examples/streamlit_heatmap.py`.  
Repo: `streamlit/heatmap_streamlit_demo.py`.
