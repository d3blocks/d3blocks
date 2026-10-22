"""Advanced treemap: size vs count, tooltips, animals sample.

Requires: d3blocks 2.3.0+
Run: python treemap_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")

# 1) Sized by weight
d3.treemap(df, value="size", filepath="treemap_size.html", title="Energy — by size")

# 2) Equal leaf count mode
d3.treemap(df, value="count", filepath="treemap_count.html", title="Energy — by count")

# 3) Tooltips on nodes
d3b = D3Blocks(chart="treemap", frame=False)
df2 = d3b.import_example("energy")
d3b.set_node_properties(df2)
if "Bio-conversion" in d3b.node_properties:
    d3b.node_properties["Bio-conversion"]["tooltip"] = "Title: Bio conversion Operations"
d3b.set_edge_properties(df2)
d3b.show(filepath="treemap_tooltip.html", title="Energy — tooltips")

# 4) Animals hierarchy sample when available
try:
    d3c = D3Blocks()
    animals = d3c.import_example("animals")
    d3c.treemap(animals, value="size", filepath="treemap_animals.html", title="Animals")
except Exception:
    pass
