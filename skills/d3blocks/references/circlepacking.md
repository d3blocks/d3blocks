# Circlepacking

Hierarchy as **nested circles** (space-filling). Same hierarchical edge idea as treemap/tree.

## Input

| Form | Columns |
|------|---------|
| Edge list | `source`, `target`, `weight` |
| Levels | `level0`, `level1`, `level2`, … and `weight` |

Samples: `energy`, `stormofswords`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `size` | `'sum'` | `'sum'` (edge weights) or `'constant'` |
| `speed` | `750` | Zoom animation (ms) |
| `zoom` | `'click'` | `'click'` or `'mouseover'` |
| `border` | dict | `color`, `width`, `fill`, `padding` |
| `font` | dict | `size`, `type`, optional colour keys |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` / `figsize` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.circlepacking
```

## vs treemap / tree

- **circlepacking** — nested circles  
- **treemap** — nested rectangles  
- **tree** — linked hierarchy diagram  

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('energy')
d3.circlepacking(df, filepath='circlepacking.html')
```

### Layout knobs

```python
d3.circlepacking(
    df,
    size='sum',
    zoom='click',
    speed=750,
    border={'color': '#FFFFFF', 'width': 1.5, 'fill': '#FFFFFF', 'padding': 5},
    font={'size': 20, 'type': 'sans-serif'},
)
```

### HTML for embedding

```python
html = d3.circlepacking(
    df,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/circlepacking_advanced.py`, `examples/streamlit_circlepacking.py`.  
Repo: `streamlit/circlepacking_streamlit_demo.py`.
