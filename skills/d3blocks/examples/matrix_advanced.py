"""Advanced matrix: scale, cmap, stroke.

Requires: d3blocks 2.3.0+
Run: python matrix_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")
df = d3.vec2adjmat(df["source"], df["target"], weight=df["weight"])

d3.matrix(df, filepath="matrix_default.html", title="Energy matrix")
d3.matrix(
    df,
    scale=True,
    cmap="interpolateViridis",
    stroke="black",
    fontsize=11,
    filepath="matrix_scaled.html",
    title="Energy matrix — scaled",
)
