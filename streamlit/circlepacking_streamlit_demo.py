"""
Minimal Streamlit demo: embed a d3blocks circlepacking chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run circlepacking_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch"). height="content" is unreliable because the
  chart uses position:fixed and contributes almost no document-flow height.
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Import your data here
# =============================================================================
@st.cache_data
def load_data():
    d3 = D3Blocks()
    return d3.import_example("energy")

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - Circlepacking", layout="wide")
df = load_data()

# =============================================================================
# Sidebar
# =============================================================================
st.sidebar.subheader("Layout")
size = st.sidebar.selectbox("Node size", ["sum", "constant"], index=0)
zoom = st.sidebar.selectbox("Zoom trigger", ["click", "mouseover"], index=0)
speed = st.sidebar.slider("Zoom speed (ms)", 100, 2500, 750, 50)
padding = st.sidebar.slider("Padding", 0, 40, 5, 1)
font_size = st.sidebar.slider("Font size", 8, 48, 20, 1)
border_width = st.sidebar.slider("Border width", 0.0, 6.0, 1.5, 0.5)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks side panels", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)
dark_mode = st.sidebar.checkbox("Dark mode", value=False)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks circlepacking
# =============================================================================
@st.cache_data(show_spinner="Building circlepacking...")
def build_circlepacking_html(size, zoom, speed, padding, font_size, border_width, show_side_panel, show_top_panel, dark_mode):
    d3 = D3Blocks()
    html = d3.circlepacking(
        df,
        size=size,
        zoom=zoom,
        speed=speed,
        border={"color": "#FFFFFF", "width": border_width, "fill": "#FFFFFF", "padding": padding},
        font={"size": font_size, "color": "#000000", "type": "Source Serif Pro", "outlinecolor": "#FFFFFF"},
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_circlepacking_html(
    size, zoom, speed, padding, font_size, border_width,
    show_side_panel, show_top_panel, dark_mode,
)
st.caption("Interactive circle packing hierarchy powered by D3Blocks and controlled by Streamlit.")
st.iframe(html, height=height, width="stretch")
