"""Advanced imageslider: before/after sample images.

Requires: d3blocks 2.3.0+ and network for internet examples
Run: python imageslider_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
before, after = d3.import_example("southern_nebula_internet")
d3.imageslider(before, after, filepath="imageslider_nebula.html")
d3.imageslider(
    before,
    after,
    scale=True,
    figsize=[500, 500],
    filepath="imageslider_nebula_sized.html",
)
