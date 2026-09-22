"""Minimal Streamlit demo for d3blocks Timeseries.

Run: streamlit run timeseries_streamlit_demo.py
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="Timeseries – D3Blocks", layout="wide")
st.title("Timeseries – D3Blocks")

# =============================================================================
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.header("Chart settings")
    dark_mode = st.checkbox("Dark mode", value=False)
    fontsize = st.slider("Font size", min_value=8, max_value=24, value=10, step=1)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")
    height = st.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build chart
# =============================================================================
d3 = D3Blocks()
df = d3.import_example("climate")
html = d3.timeseries(
    df,
    datetime="date",
    dt_format="%Y-%m-%d",
    fontsize=fontsize,
    show_side_panel=show_side_panel,
    show_top_panel=show_top_panel,
    dark_mode=dark_mode,
    color_background="streamlit",
    showfig=False,
    return_html=True,
    filepath=None,
)

# =============================================================================
# Display chart
# =============================================================================
st.iframe(html, height=height)
