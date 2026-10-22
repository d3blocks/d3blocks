"""Advanced particles: shapes, spacing, cmap.

Requires: d3blocks 2.3.0+
Run: python particles_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
d3.particles("D3Blocks", filepath="particles_default.html")
d3.particles(
    "Hello",
    radius=4,
    fontsize=180,
    spacing=8,
    shape="square",
    square_scale=1.5,
    cmap="Turbo",
    color_background="#111111",
    filepath="particles_square.html",
)
