"""Minimal Streamlit demo for d3blocks Chord.

Run: streamlit run chord_streamlit_demo.py
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="Chord – D3Blocks", layout="wide")
st.title("Chord – D3Blocks")

# =============================================================================
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.header("Chart settings")
    ordering = st.radio("Ordering", options=["ascending", "descending", ""], format_func=lambda x: x or "none", horizontal=True)
    fontsize = st.slider("Font size", min_value=6, max_value=24, value=10, step=1)
    dark_mode = st.checkbox("Dark mode", value=False)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")
    height = st.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build chart
# =============================================================================
d3 = D3Blocks()
df = d3.import_example("energy")
html = d3.chord(
    df,
    ordering=ordering,
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
