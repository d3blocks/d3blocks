"""Advanced timeseries: climate sample, whitelist, formatting.

Requires: d3blocks 2.3.0+
Run: python timeseries_advanced.py
"""
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("climate")

# 1) All series
d3.timeseries(
    df,
    datetime="date",
    dt_format="%Y-%m-%d",
    filepath="timeseries_climate.html",
    title="Climate",
)

# 2) Filtered series names (if columns match)
d3.timeseries(
    df,
    datetime="date",
    dt_format="%Y-%m-%d",
    whitelist=None,
    fontsize=12,
    cmap="Set2",
    filepath="timeseries_climate_styled.html",
    title="Climate — styled",
)
