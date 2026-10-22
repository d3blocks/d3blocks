"""Advanced tree: hierarchy levels, styled node properties.

Requires: d3blocks 2.3.0+
Run: python tree_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Default hierarchy
d3.tree(df, filepath="tree_default.html", title="Energy tree")

# 2) Shorter links, custom hierarchy expansion
d3.tree(
    df,
    hierarchy=[1, 2, 3, 4, 5],
    link_length=140,
    font={"size": 11},
    figsize=[1000, 750],
    filepath="tree_compact.html",
    title="Energy tree — compact",
)

# 3) Node property edits
d3b = D3Blocks(chart="tree", frame=False)
df2 = d3b.import_example("energy")
d3b.set_node_properties(df2)
bio = d3b.node_properties.get("Bio-conversion")
if bio is not None:
    bio["size"] = 30
    bio["color"] = "#000000"
    bio["opacity"] = 0.5
loss = d3b.node_properties.get("Losses")
if loss is not None:
    loss["color"] = "#FF0000"
    loss["size"] = 15
d3b.set_edge_properties(df2)
d3b.show(
    hierarchy=[1, 2, 3, 4, 5, 6, 7, 8],
    filepath="tree_styled.html",
    title="Energy tree — styled nodes",
)
