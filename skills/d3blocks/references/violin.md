# Violin

Distribution of a **numeric** variable across **groups** (alternative to a boxplot). Points can carry size, colour, and tooltips.

## Input

Not a single DataFrame argument — pass arrays (same style as scatter):

| Argument | Role |
|----------|------|
| `x` | Group / class labels (1d) |
| `y` | Numeric values (1d, same length as `x`) |
| `size` / `color` / `opacity` / `stroke` / `tooltip` | Optional per-point encodings |
| `x_order` | Optional ordered list of group labels on the x-axis |
| `df` | Optional aligned DataFrame for extra context |

Built-in sample: `d3.import_example('cancer')` (e.g. `labx` × `age`).

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `x`, `y` | required | Group labels and values |
| `bins` | `50` | Histogram bins inside each violin |
| `jitter` | `40` | Point jitter |
| `size` | | Scalar or array |
| `color` | | Hex, array, or cmap-based |
| `cmap` | `'inferno'` | |
| `opacity` / `stroke` | `0.6` / `'#000000'` | |
| `tooltip` | `None` | Per-point HTML strings |
| `fontsize` / `fontsize_axis` | `12` | |
| `x_order` | `None` | Category order on x-axis |
| `ylim` | `[None, None]` | |
| `figsize` | `[None, None]` | e.g. `[900, None]` |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.violin
```

Do **not** call `d3.violin(df)`. Always pass `x=` and `y=`.

## Examples

### Cancer ages by type

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('cancer')
tooltip = df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values

d3.violin(
    x=df['labx'].values,
    y=df['age'].values,
    size=df['survival_months'].values / 10,
    tooltip=tooltip,
    bins=50,
    x_order=['acc', 'kich', 'brca', 'lgg', 'blca', 'coad', 'ov'],
    filepath='violin.html',
    figsize=[900, None],
)
```

### Edit edge properties then show

```python
d3 = D3Blocks(chart='Violin', frame=True)
df = d3.import_example('cancer')
d3.set_edge_properties(
    x=df['labx'].values,
    y=df['age'].values,
    size=df['survival_months'].values / 10,
    x_order=['acc', 'kich', 'brca', 'lgg', 'blca', 'coad', 'ov'],
)
d3.edge_properties.loc[0, 'size'] = 50
d3.edge_properties.loc[0, 'color'] = '#000000'
d3.edge_properties.loc[0, 'tooltip'] = 'I am adjusted!'
d3.show()
```

### HTML for embedding

```python
html = d3.violin(
    x=df['labx'].values,
    y=df['age'].values,
    bins=50,
    jitter=40,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
    figsize=[900, None],
)
```

## Full runnable examples

`examples/violin_advanced.py`, `examples/streamlit_violin.py`.  
Repo: `streamlit/violin_streamlit_demo.py`.
