# Matrix

Interactive **matrix / heatmap-style** view of a DataFrame. Index and column names label axes; values colour the cells. Related to `heatmap` but with a simpler matrix API (scale, vmin/vmax, stroke).

## Input

`pd.DataFrame` used as a matrix:

- **Index** → row labels  
- **Columns** → column labels  
- **Values** → cell intensities  

Convert edge-list samples such as `energy` to an adjacency matrix with `d3.vec2adjmat` before calling `matrix`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `scale` | `False` | Scale values into a display range |
| `stroke` | `'red'` | Hover rectangle colour |
| `vmin` / `vmax` | `None` | Colour scale caps |
| `cmap` | `'interpolateInferno'` | d3-scale-chromatic name |
| `fontsize` | `10` | Axis labels |
| `description` | `None` | Optional description text |
| `figsize` | `[700, 500]` | |
| `return_html` / `filepath` / `showfig` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.matrix
```

## vs heatmap

- **matrix** — lighter matrix colouring API  
- **heatmap** — clustering, `cluster_params`, network-oriented colouring  

## Examples

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'])
d3.matrix(df, filepath='matrix.html')
```

```python
d3.matrix(df, scale=True, cmap='interpolateViridis', stroke='black')
```

```python
html = d3.matrix(df, showfig=False, return_html=True, filepath=None)
```

## Full runnable examples

`examples/matrix_advanced.py`, `examples/streamlit_matrix.py`.
