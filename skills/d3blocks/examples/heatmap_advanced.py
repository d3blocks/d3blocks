"""Advanced heatmap: clustering params, label colours, bigbang sample.

Requires: d3blocks 2.3.0+
Run: python heatmap_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()

# 1) Storm of Swords adjacency
df = d3.import_example("stormofswords")
d3.heatmap(df, filepath="heatmap_sos.html", title="Storm of Swords")

# 2) Custom cluster parameters on energy
df_e = d3.import_example("energy")
d3.heatmap(
    df_e,
    cluster_params={
        "evaluate": "dbindex",
        "metric": "hamming",
        "linkage": "complete",
        "normalize": False,
        "min_clust": 3,
        "max_clust": 15,
    },
    filepath="heatmap_energy_cluster.html",
    title="Energy — custom clusters",
)

# 3) Colour by explicit labels / hex (bigbang)
df_b = d3.import_example("bigbang")
d3.heatmap(
    df_b,
    color=[1, 1, 1, 2, 2, 2, 3],
    filepath="heatmap_bigbang_labels.html",
    title="Big Bang — label colours",
)
d3.heatmap(
    df_b,
    color=["#FFF000", "#FFF000", "#FFF000", "#000FFF", "#000FFF", "#000FFF", "#000FFF"],
    filepath="heatmap_bigbang_hex.html",
    title="Big Bang — hex colours",
)
