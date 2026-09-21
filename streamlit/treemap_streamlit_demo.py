"""Minimal Streamlit demo for d3blocks Treemap.

Run: streamlit run treemap_streamlit_demo.py
"""

import streamlit as st
from d3blocks import D3Blocks
# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="Treemap – D3Blocks", layout="wide")
st.title("Treemap – D3Blocks")

# =============================================================================
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.header("Chart settings")
    value_mode = st.radio("Value mode", options=["size", "count"], horizontal=True)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    dark_mode = st.checkbox("Dark mode", value=False)

# =============================================================================
# Build chart
# =============================================================================
d3 = D3Blocks()
df = d3.import_example("energy")
html = d3.treemap(df, value=value_mode, show_side_panel=show_side_panel, show_top_panel=show_top_panel, dark_mode=dark_mode, color_background="streamlit", showfig=False, return_html=True, filepath=None)

# =============================================================================
# Display chart
# =============================================================================
st.iframe(html)
