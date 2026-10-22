# Imageslider

**Before / after** image comparison with a draggable slider.

## Input

Two image paths (or URLs returned by `import_example`):

| Argument | Role |
|----------|------|
| `img_before` | Left / “before” image |
| `img_after` | Right / “after” image |

Samples:

```python
img_before, img_after = d3.import_example('southern_nebula_internet')
# or 'southern_nebula', 'unsplash_before'/after via other examples
```

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `scale` | `True` | Scale pixel values into [0, 255] |
| `colorscale` | `-1` | Colour scaling; `-1` = untouched |
| `background` / `color_background` | dark defaults | |
| `dark_mode` | `True` | |
| `figsize` | `[None, None]` | |
| `return_html` / `filepath` / `showfig` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.imageslider
```

## Examples

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
before, after = d3.import_example('southern_nebula_internet')
d3.imageslider(before, after, filepath='imageslider.html')
```

```python
d3.imageslider(before, after, scale=True, colorscale=2, figsize=[400, 400])
```

```python
html = d3.imageslider(
    before, after,
    dark_mode=True,
    color_background='streamlit',
    showfig=False,
    return_html=True,
)
```

## Full runnable examples

`examples/imageslider_advanced.py`, `examples/streamlit_imageslider.py`.  
Repo: `streamlit/imageslider_streamlit_demo.py`.
