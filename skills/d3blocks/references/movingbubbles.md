# Movingbubbles

Animated bubbles that move between **states** over **time**. Shows when entities change state and whether clusters form at certain times. Force-directed colliding nodes.

## Input

DataFrame with (default column names; override with kwargs):

| Column | Default name | Role |
|--------|--------------|------|
| Datetime | `datetime` | When the event occurs |
| Sample | `sample_id` | Entity id (one sample can visit many states over time, not two states at the same instant) |
| State | `state` | State / location / category at that time |

Built-in sample:

```python
df = d3.import_example(
    'random_time',
    n=10000,          # events
    c=300,            # distinct sample ids
    date_start='1-1-2000 00:10:05',
    date_stop='1-1-2000 23:59:59',
)
```

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `datetime` / `sample_id` / `state` | column names | Rename if your CSV differs |
| `dt_format` | `'%d-%m-%Y %H:%M:%S'` | Parsing format for datetime strings |
| `center` | `None` | Center this state category in the layout |
| `size` | `5` | Scalar, per-row array, or `{sample_id: size}` |
| `color` | `None` | Hex, array, `{sample_id: hex}`, or `None` → cmap by sample |
| `opacity` / `stroke` | `0.6` / `'#000000'` | Scalar, array, or per-sample dict |
| `color_method` | `'state'` | `'state'` or `'node'` (sample) |
| `cmap` | `'Set1'` | |
| `standardize` | `'samplewise'` | Time standardization mode |
| `timedelta` | `'minutes'` | Aggregation unit (`seconds` / `minutes` / `days`) |
| `damper` | `1` | Motion damping |
| `speed` | `{"slow": 750, "medium": 250, "fast": 25, "superfast": 5}` | Playback delays (ms) |
| `fontsize` | `14` | State labels |
| `note` / `time_notes` | `None` | Optional annotations |
| `node_text_inside` | `True` | Label placement |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` / `figsize` | standard | |

Live signature:

```bash
python -m pydoc d3blocks.D3Blocks.movingbubbles
```

## When to prefer movingbubbles

- Entity trajectories through discrete states over time → **movingbubbles**
- Continuous series of numeric values over time → **timeseries**
- Static x/y of samples → **scatter**

## Examples

### Basic

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example(
    'random_time', n=10000, c=300,
    date_start='1-1-2000 00:10:05', date_stop='1-1-2000 23:59:59',
)
d3.movingbubbles(
    df,
    speed={'slow': 1000, 'medium': 200, 'fast': 50, 'superfast': 20},
    filepath='movingbubbles.html',
)
```

### Per-sample size and colour

```python
import random

size = {i: random.randint(2, 15) for i in range(1, 100)}
color = {1: '#FF0000', 3: '#000FFF'}
d3.movingbubbles(df, color=color, size=size, color_method='node')
```

### Colour states, then edit and show

```python
d3 = D3Blocks(chart='movingbubbles', frame=False)
df = d3.import_example('random_time', n=1000, c=100,
                       date_start='1-1-2000 00:10:05', date_stop='1-1-2000 23:59:59')
d3.set_node_properties(df['state'])
d3.node_properties.get('Sleeping')['color'] = '#000000'
d3.set_edge_properties(df)
d3.show(title='Movingbubbles with adjusted colours')
```

### HTML for embedding

```python
html = d3.movingbubbles(
    df,
    damper=1.0,
    timedelta='minutes',
    color_method='state',
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

In this skill: `examples/movingbubbles_advanced.py` and `examples/streamlit_movingbubbles.py`.  
Repo demo: `streamlit/movingbubbles_streamlit_demo.py`.
