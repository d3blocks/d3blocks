# Particles

Turn a **text string** into interactive bouncing particles (mouse/touch). Decorative / branding chart.

## Input

A single string, e.g. `"D3Blocks"`.

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `text` | required | String to visualize |
| `radius` | `3` | Particle size |
| `collision` | `0.1` | Collision response |
| `fontsize` | `250` | Larger text → also widen figure |
| `spacing` | `10` | Higher → fewer particles |
| `cmap` | `'Set2'` | Particle colours |
| `color_background` | `'#000000'` | |
| `shape` | `'circle'` | `'circle'` or `'square'`/`'rect'` |
| `mouse_radius` | `50` | Hover disturbance radius |
| `square_scale` | `1.5` | Size factor for squares |
| `figsize` | `[900, 200]` | |
| `return_html` / `filepath` / `showfig` | standard | |

```bash
python -m pydoc d3blocks.D3Blocks.particles
```

## Examples

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
d3.particles('D3Blocks', filepath='particles.html')
```

```python
d3.particles(
    'Hello',
    radius=4,
    fontsize=200,
    spacing=8,
    shape='square',
    cmap='Turbo',
    color_background='#111111',
)
```

```python
html = d3.particles('D3Blocks', showfig=False, return_html=True, filepath=None)
```

## Full runnable examples

`examples/particles_advanced.py`, `examples/streamlit_particles.py`.
