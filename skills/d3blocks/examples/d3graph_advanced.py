"""Advanced d3graph: scaler, node property edits.

Requires: d3blocks 2.3.0+
Run: python d3graph_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Default force layout
d3.d3graph(df, filepath="d3graph_default.html", title="Energy network")

# 2) Minmax scaler
d3.d3graph(df, scaler="minmax", filepath="d3graph_minmax.html", title="Energy — minmax")

# 3) Enlarge a node and redraw
d3.d3graph(df, showfig=False)
d3.D3graph.set_node_properties(color=None)
if "Solar" in d3.D3graph.node_properties:
    d3.D3graph.node_properties["Solar"]["size"] = 30
d3.D3graph.show(filepath="d3graph_solar.html")
