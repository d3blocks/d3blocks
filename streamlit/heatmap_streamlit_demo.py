"""Minimal Streamlit demo for d3blocks Heatmap.

Run: streamlit run heatmap_streamlit_demo.py
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="Heatmap – D3Blocks", layout="wide")
st.title("Heatmap – D3Blocks")

# =============================================================================
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.header("Chart settings")
    fontsize = st.slider("Font size", min_value=6, max_value=28, value=10, step=1)
    dark_mode = st.checkbox("Dark mode", value=False)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")

# =============================================================================
# Build chart
# =============================================================================
d3 = D3Blocks()
df = d3.import_example("stormofswords")
html = d3.heatmap(
    df,
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
st.iframe(html)
