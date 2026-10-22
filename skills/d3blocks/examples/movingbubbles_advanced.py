"""Advanced movingbubbles: speed, state colours, per-sample size/colour.

Requires: d3blocks 2.3.0+
Run: python movingbubbles_advanced.py
"""
import random
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example(
    "random_time",
    n=3000,
    c=80,
    date_start="1-1-2000 00:10:05",
    date_stop="1-1-2000 23:59:59",
)

# 1) Default-ish with explicit playback speeds
d3.movingbubbles(
    df,
    speed={"slow": 1000, "medium": 200, "fast": 50, "superfast": 20},
    timedelta="minutes",
    color_method="state",
    size=5,
    opacity=0.6,
    filepath="movingbubbles_default.html",
    title="Random day — by state",
)

# 2) Per-sample size and a few highlighted samples
size = {i: random.randint(3, 14) for i in range(1, 81)}
color = {1: "#FF0000", 3: "#000FFF", 7: "#2ca02c"}
d3.movingbubbles(
    df,
    size=size,
    color=color,
    color_method="node",
    damper=1.2,
    fontsize=12,
    filepath="movingbubbles_per_sample.html",
    title="Random day — per-sample size/colour",
)

# 3) Edit state colours then show
d3b = D3Blocks(chart="movingbubbles", frame=False)
df2 = d3b.import_example(
    "random_time",
    n=1500,
    c=40,
    date_start="1-1-2000 00:10:05",
    date_stop="1-1-2000 23:59:59",
)
d3b.set_node_properties(df2["state"])
if d3b.node_properties.get("Sleeping") is not None:
    d3b.node_properties["Sleeping"]["color"] = "#000000"
d3b.set_edge_properties(df2)
d3b.show(
    filepath="movingbubbles_state_colours.html",
    title="Random day — Sleeping highlighted",
)
