# Timeseries

Interactive multi-series **line chart** over time. One datetime column plus numeric series columns.

## Input

DataFrame with:

| Column | Role |
|--------|------|
| Datetime column (name via `datetime=`) | Time axis |
| Other numeric columns | One line each (unless filtered by `whitelist`) |

Built-in sample: `d3.import_example('climate')` (use `datetime='date'`, `dt_format='%Y-%m-%d'`).

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `datetime` | `None` | Column name for timestamps |
| `dt_format` | | e.g. `'%Y-%m-%d'` or `'%d-%m-%Y %H:%M:%S'` |
| `sort_on_date` | `True` | Sort rows by datetime |
| `whitelist` | `None` | Keep only columns whose names contain this substring |
| `fontsize` | `14` | |
| `cmap` | `'Set1'` | Series colours |
| `figsize` | `[None, None]` | Auto-size recommended |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.timeseries
```

## vs movingbubbles

- **timeseries** — continuous numeric series vs time  
- **movingbubbles** — discrete entity **states** over time (`datetime`, `sample_id`, `state`)

## Examples

### Climate

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('climate')
d3.timeseries(
    df,
    datetime='date',
    dt_format='%Y-%m-%d',
    filepath='timeseries.html',
)
```

### Filter series names

```python
d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', whitelist='temp')
```

### HTML for embedding

```python
html = d3.timeseries(
    df,
    datetime='date',
    dt_format='%Y-%m-%d',
    fontsize=12,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/timeseries_advanced.py`, `examples/streamlit_timeseries.py`.  
Repo: `streamlit/timeseries_streamlit_demo.py`.
