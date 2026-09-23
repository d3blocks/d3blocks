"""
Minimal Streamlit demo: embed a d3blocks d3graph chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run d3graph_streamlit_demo.py

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
st.set_page_config(page_title="D3Blocks - D3graph", layout="wide")
df = load_data()

# =============================================================================
# Sidebar
# =============================================================================
st.sidebar.subheader("Network")
color = st.sidebar.selectbox("Node color", ["cluster", None], index=0)
size = st.sidebar.selectbox("Node size", ["degree", 10], index=0)
collision = st.sidebar.slider("Collision", 0.1, 2.0, 0.5, 0.05)
charge = st.sidebar.slider("Charge", 50, 2000, 600, 50)
show_slider = st.sidebar.checkbox("Show edge-threshold slider", value=True)
show_density = st.sidebar.checkbox("Show density layer", value=False)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks side panels", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)
dark_mode = st.sidebar.checkbox("Dark mode", value=False)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks d3graph
# =============================================================================
@st.cache_data(show_spinner="Building d3graph...")
def build_d3graph_html(color, size, collision, charge, show_slider, show_density, show_side_panel, show_top_panel, dark_mode):
    d3 = D3Blocks()
    html = d3.d3graph(
        df,
        color=color,
        size=size,
        collision=collision,
        charge=charge,
        show_slider=show_slider,
        show_density=show_density,
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
html = build_d3graph_html(
    color, size, collision, charge, show_slider, show_density,
    show_side_panel, show_top_panel, dark_mode,
)
st.caption("Interactive force-directed network powered by D3Blocks / d3graph and controlled by Streamlit.")
st.iframe(html, height=height, width="stretch")
