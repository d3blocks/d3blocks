"""Advanced maps: markers, country choropleth, regional names.

Requires: d3blocks 2.3.0+
Run: python maps_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()

# 1) Surf spot markers
df = d3.import_example("surfspots")
d3.maps(df, filepath="maps_surfspots.html", title="Surf spots")

# 2) Country-only choropleth
d3.maps(
    country_names=["Netherlands", "France", "Germany"],
    cmap="Set1",
    filepath="maps_countries.html",
    title="Selected countries",
)

# 3) Markers without overseas territories
d3.maps(
    df,
    include_overseas=False,
    filepath="maps_surf_no_overseas.html",
    title="Surf spots — no overseas",
)
