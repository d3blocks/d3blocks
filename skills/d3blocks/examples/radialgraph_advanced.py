"""Advanced radialgraph: auto vs explicit center, layout knobs, significance.

Requires: d3blocks 2.3.0+
Run: python radialgraph_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Auto focus (highest-degree node), default rings
d3.radialgraph(
    df,
    center=None,
    filepath="radialgraph_auto_center.html",
    title="Energy network — auto center",
    dark_mode=True,
)

# 2) Explicit focus + tighter rings and stronger charge
d3.radialgraph(
    df,
    center="Solar",
    ring_spacing=85,
    auto_ring_spacing=True,
    radial_strength=0.9,
    charge=-160,
    color="cluster",
    size="degree",
    opacity="degree",
    edge_opacity="weight",
    min_weight=1.0,
    show_side_panel=True,
    show_top_panel=True,
    show_bottom_panel=True,
    filepath="radialgraph_solar.html",
    title="Energy network — focus Solar",
)

# 3) PageRank significance on the Python side (optional; may be slower)
d3.radialgraph(
    df,
    center="Nuclear",
    significance_test="pagerank",
    significance_alpha=0.05,
    color="cluster",
    size="degree",
    expand_all_on_load=False,
    filepath="radialgraph_nuclear_pagerank.html",
    title="Energy network — Nuclear + PageRank",
)
