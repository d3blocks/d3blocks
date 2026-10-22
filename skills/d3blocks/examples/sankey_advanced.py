"""Advanced sankey: layout knobs, custom node colours, property edits.

Requires: d3blocks 2.3.0+
Run: python sankey_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Default energy flows
d3.sankey(df, filepath="sankey_default.html", title="Energy flows")

# 2) Left-aligned nodes, source-coloured links
d3.sankey(
    df,
    link={
        "color": "source",
        "stroke_opacity": 0.55,
        "color_static": "#d3d3d3",
    },
    node={
        "align": "left",
        "width": 18,
        "padding": 12,
        "color": "currentColor",
    },
    fontsize=11,
    figsize=[1100, 800],
    margin={"top": 10, "right": 10, "bottom": 10, "left": 10},
    filepath="sankey_left_source.html",
    title="Energy flows — left align, source links",
)

# 3) Custom node colours via set_node/edge_properties, then show
d3b = D3Blocks(chart="Sankey", frame=True)
df2 = d3b.import_example("energy")
d3b.set_node_properties(
    df2,
    color={
        "Nuclear": "#FF0000",
        "Wind": "#1f77b4",
        "Electricity grid": "#7FFFD4",
        "Bio-conversion": "#2ca02c",
        "Industry": "#333333",
    },
)
d3b.set_edge_properties(df2, color="target", opacity="target")
d3b.show(
    filepath="sankey_custom_nodes.html",
    title="Energy flows — custom node colours",
)
