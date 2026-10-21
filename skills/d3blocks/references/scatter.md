# Scatter

Interactive scatter: pan, zoom, brush, multiple coordinate systems with radio transitions, and optional association exploration when `df` is provided.

## Input

**Required:** 1d arrays `x` and `y` (same length).

**Optional coordinate systems:** `x1`/`y1`, `x2`/`y2`, `x3`/`y3` with `label_radio` for transitions.

**Optional:** `df` — DataFrame aligned by index/row with `x`/`y` for tooltips and associations.

Built-in sample: `d3.import_example('cancer')` (columns include `tsneX`, `tsneY`, `PC1`, `PC2`, `labx`, `age`, …).

Do **not** call `d3.scatter(df)`. Always pass `x=` and `y=`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `x`, `y` | required | Primary coordinates |
| `x1`…`y3` | `None` | Extra coordinate systems |
| `size` | `3` | Scalar or array |
| `color` | `'#002147'` | Hex, array of hex, or categorical labels (with `cmap`) |
| `stroke` | `'#000000'` | Point edge colour |
| `opacity` | `0.6` | Scalar or array in [0, 1] |
| `tooltip` | `None` | List of strings (HTML allowed) |
| `c_gradient` | `'opaque'` | Density gradient; `None` to disable |
| `cmap` | `'tab20'` | For categorical colour |
| `scale` | `False` | Scale points |
| `jitter` | `None` | Small random jitter |
| `label_radio` | `['(x, y)', …]` | Labels for coord-system radio buttons |
| `xlim` / `ylim` | auto | Axis limits |
| `df` | `None` | Row-aligned properties |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` | `True` | |
| `color_background` | `None` | e.g. `'streamlit'` |
| `return_html` | `False` | |
| `filepath` | `'scatter.html'` | |

Common flags: `title`, `figsize`, `showfig`, `overwrite`, `notebook`, `save_button`, `reset_properties`.

## Examples

### Sample data

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('cancer')
# or a small frame:
# df = pd.DataFrame({... tsneX, tsneY, labx, age, PC1, PC2 ...})
```

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks(chart='Scatter')
d3.scatter(x=df['tsneX'].values, y=df['tsneY'].values, df=df)
```

### Return HTML

```python
html = d3.scatter(
    x=df['tsneX'].values,
    y=df['tsneY'].values,
    df=df,
    return_html=True,
    showfig=False,
    filepath=None,
)
```

### Color by category

```python
d3.scatter(
    df['tsneX'].values,
    df['tsneY'].values,
    color=df['labx'].values,
    opacity=0.5,
    df=df,
)
```

### Size by numeric column

```python
d3.scatter(
    df['tsneX'].values,
    df['tsneY'].values,
    size=df['age'].fillna(1).values / 10,
    df=df,
)
```

### Two coordinate systems (t-SNE ↔ PCA)

```python
d3.scatter(
    x=df['tsneX'].values,
    y=df['tsneY'].values,
    x1=df['PC1'].values,
    y1=df['PC2'].values,
    label_radio=['tSNE', 'PCA'],
    df=df,
)
```

### Size, color, opacity, tooltip, scale, two systems

```python
d3.scatter(
    x=df['tsneX'].values,
    y=df['tsneY'].values,
    x1=df['PC1'].values,
    y1=df['PC2'].values,
    size=df['age'].fillna(1).values / 10,
    color=df['labx'].values,
    opacity=0.5,
    tooltip=df['labx'].values,
    scale=True,
    label_radio=['tSNE', 'PCA'],
    df=df,
)
```

### Streamlit

See `references/streamlit.md` and `streamlit/scatter_streamlit_demo.py`.

## Full runnable examples

In this skill: `examples/scatter_advanced.py and examples/streamlit_scatter.py`.
