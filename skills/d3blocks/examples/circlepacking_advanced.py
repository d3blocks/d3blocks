"""Advanced circlepacking: size mode, zoom, border/font.

Requires: d3blocks 2.3.0+
Run: python circlepacking_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Default sum sizing
d3.circlepacking(df, filepath="circlepacking_sum.html", title="Energy circles")

# 2) Constant leaf size + mouseover zoom
d3.circlepacking(
    df,
    size="constant",
    zoom="mouseover",
    speed=600,
    border={"color": "#FFFFFF", "width": 1.5, "fill": "#FFFFFF", "padding": 5},
    font={"size": 18, "type": "sans-serif"},
    filepath="circlepacking_constant.html",
    title="Energy circles — constant",
)
