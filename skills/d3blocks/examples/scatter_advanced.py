"""Advanced scatter: multi-coordinate systems, encodings, rich tooltips.

Requires: pip install d3blocks
Run: python scatter_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks(chart="Scatter")
df = d3.import_example("cancer")

# Rich HTML tooltips (aligned with rows)
tooltip = (
    df["labx"].astype(str)
    + " <br> Survival: "
    + df["survival_months"].astype(str).str[:4]
    + " <br> Age: "
    + df["age"].fillna(-1).astype(int).astype(str)
)

# t-SNE as primary view, PCA as second; radio buttons switch with animation
d3.scatter(
    x=df["tsneX"].values,
    y=df["tsneY"].values,
    x1=df["PC1"].values,
    y1=df["PC2"].values,
    size=df["survival_months"].fillna(1).clip(lower=1).values / 10,
    color=df["labx"].values,
    opacity=0.55,
    stroke="#222222",
    tooltip=tooltip.values,
    scale=True,
    c_gradient="opaque",
    label_radio=["tSNE", "PCA"],
    df=df,
    title="Cancer embeddings — tSNE / PCA",
    filepath="scatter_advanced.html",
    show_side_panel=True,
    show_top_panel=True,
    dark_mode=True,
)

# Optional: return HTML for notebooks / custom hosts
# html = d3.scatter(..., return_html=True, showfig=False, filepath=None)
