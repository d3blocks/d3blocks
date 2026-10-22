"""Advanced elasticgraph: clusters, node/edge edits via Elasticgraph.D3graph.

Requires: d3blocks 2.3.0+
Run: python elasticgraph_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Clustered force layout
d3.elasticgraph(df, filepath="elasticgraph_default.html", title="Energy elastic")

# 2) Stronger charge / hull
d3.elasticgraph(
    df,
    charge=600,
    hull_offset=20,
    collision=0.5,
    filepath="elasticgraph_charge.html",
    title="Energy elastic — charge",
)

# 3) Edit underlying d3graph properties
d3.elasticgraph(df, showfig=False)
np = d3.Elasticgraph.D3graph.node_properties
if "Wind" in np:
    np["Wind"]["size"] = 20
ep = d3.Elasticgraph.D3graph.edge_properties
key = ("Wind", "Electricity_grid")
if key in ep:
    ep[key]["label"] = "Test"
d3.Elasticgraph.show(filepath="elasticgraph_edited.html")
