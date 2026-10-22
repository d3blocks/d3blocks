"""Advanced violin: group order, size/tooltip encodings, property edits.

Requires: d3blocks 2.3.0+
Run: python violin_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("cancer")

tooltip = (
    df["labx"].astype(str).values
    + " <br /> Survival: "
    + df["survival_months"].astype(str).values
)
x_order = ["acc", "kich", "brca", "lgg", "blca", "coad", "ov"]

# 1) Full encodings
d3.violin(
    x=df["labx"].values,
    y=df["age"].values,
    size=df["survival_months"].values / 10,
    tooltip=tooltip,
    bins=50,
    jitter=40,
    x_order=x_order,
    filepath="violin_cancer.html",
    figsize=[900, None],
    title="Cancer age by type",
)

# 2) Edit edge properties then show
d3b = D3Blocks(chart="Violin", frame=True)
df2 = d3b.import_example("cancer")
d3b.set_edge_properties(
    x=df2["labx"].values,
    y=df2["age"].values,
    size=df2["survival_months"].values / 10,
    x_order=x_order,
)
d3b.edge_properties.loc[0, "size"] = 50
d3b.edge_properties.loc[0, "color"] = "#000000"
d3b.edge_properties.loc[0, "tooltip"] = "I am adjusted!"
d3b.edge_properties.loc[0, "fontsize"] = 30
d3b.show(filepath="violin_edited.html", title="Cancer — edited point")
