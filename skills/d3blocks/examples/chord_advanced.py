"""Advanced chord: ordering, node/edge property edits, targeted highlights.

Requires: pip install d3blocks
Run: python chord_advanced.py
"""
from d3blocks import D3Blocks

# --- 1) Editable properties, then redraw with a highlight ---
d3 = D3Blocks(chart="Chord", frame=False)
df = d3.import_example("energy")

d3.set_node_properties(df, opacity=0.25, cmap="tab20")
d3.set_edge_properties(df, color="source", opacity="source")
d3.show(
    filepath="chord_soft.html",
    title="Energy flows (soft)",
    ordering="ascending",
    fontsize=11,
    figsize=[1000, 1000],
    margin=180,
)

# Highlight Nuclear as a node
nuclear = d3.node_properties.get("Nuclear")
if nuclear is not None:
    nuclear["color"] = "#ff0000"
    nuclear["opacity"] = 1.0

# Boost the Nuclear → Thermal generation ribbon
ep = d3.edge_properties
mask = (ep["source"] == "Nuclear") & (ep["target"] == "Thermal generation")
if mask.any():
    ep.loc[mask, "color"] = "#ff0000"
    ep.loc[mask, "opacity"] = 0.9
    base = float(ep.loc[mask, "weight"].iloc[0])
    ep.loc[mask, "weight"] = max(base * 1.5, 1.0)

d3.show(
    filepath="chord_highlight_nuclear.html",
    title="Energy flows — Nuclear highlighted",
    ordering="descending",
    fontsize=12,
    figsize=[1100, 1100],
    margin=200,
    text_offset=12,
    show_side_panel=True,
    show_top_panel=True,
    dark_mode=True,
)

# --- 2) One-shot: source-target colours and room for long labels ---
d32 = D3Blocks()
d32.chord(
    df,
    color="source-target",
    opacity=0.7,
    ordering="ascending",
    fontsize=10,
    arrowhead=12,
    cmap="Set2",
    margin=250,
    text_offset=20,
    figsize=[1200, 1200],
    filepath="chord_large_labels.html",
    title="Energy flows — large margins",
)
