# Maps

Interactive **world (or regional) map** with optional **lon/lat markers** and **country choropleth** (fuzzy-matched names).

## Input

**Markers** — DataFrame (or `None` for country-only):

| Column | Required | Role |
|--------|----------|------|
| `lon` | yes (for markers) | Longitude |
| `lat` | yes | Latitude |
| `label` / `size` / `color` / `opacity` | no | Per-marker overrides |

Built-in markers: `d3.import_example('surfspots')`.

**Countries** — without markers:

```python
d3.maps(country_names=['Netherlands', 'France', 'Germany'], cmap='Set1')
```

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `df` | `None` | Marker table; empty/`None` → country-only |
| `size` / `color` / `opacity` / `label` | marker defaults | |
| `country_names` | `None` | List of names (fuzzy-matched) |
| `country_colors` / `country_opacity` / `country_values` | `None` | Choropleth styling |
| `countries` | `None` | Explicit dict of per-country style |
| `map_name` | `'world'` | Map geometry |
| `include_overseas` | `True` | Include overseas territories when relevant |
| `cmap` | `'Set2'` | |
| `show_side_panel` / `show_top_panel` | `True` | |
| `dark_mode` / `color_background` | theme | |
| `return_html` / `filepath` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.maps
```

## Examples

### Markers only (surf spots)

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example('surfspots')
d3.maps(df, filepath='maps_surf.html')
```

### Country colours, no markers

```python
d3.maps(country_names=['Netherlands', 'France', 'Germany'], cmap='Set1')
```

### Regional names (e.g. Dutch provinces)

```python
d3.maps(country_names=['Zeeland', 'Overijssel', 'Limburg'], cmap='Set2')
```

### HTML for embedding

```python
html = d3.maps(
    df,
    include_overseas=False,
    dark_mode=False,
    color_background='streamlit',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Full runnable examples

`examples/maps_advanced.py`, `examples/streamlit_maps.py`.  
Repo: `streamlit/maps_streamlit_demo.py`.
