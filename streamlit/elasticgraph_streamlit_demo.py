"""
Minimal Streamlit demo: embed a d3blocks elasticgraph chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run elasticgraph_streamlit_demo.py

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
st.set_page_config(page_title="D3Blocks - Elasticgraph", layout="wide")
df = load_data()

# =============================================================================
# Sidebar
# =============================================================================
st.sidebar.subheader("Network")
group = st.sidebar.selectbox("Node grouping", ["cluster", "None"], index=0)
if group == "None":
    group = None

collision = st.sidebar.slider("Collision", 0.1, 3.0, 0.5, 0.1)
charge = st.sidebar.slider("Charge", 50, 5000, 500, 50)
size = st.sidebar.slider("Node size", 1, 20, 4, 1)
hull_offset = st.sidebar.slider("Hull offset", 0, 60, 15, 1)
sticky = st.sidebar.checkbox("Sticky nodes", value=True)
single_click_expand = st.sidebar.checkbox("Single-click expand", value=False)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks side panels", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)
dark_mode = st.sidebar.checkbox("Dark mode", value=False)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks elasticgraph
# =============================================================================
@st.cache_data(show_spinner="Building elasticgraph...")
def build_elasticgraph_html(group, collision, charge, size, hull_offset, sticky, single_click_expand, show_side_panel, show_top_panel, dark_mode):
    d3 = D3Blocks()
    html = d3.elasticgraph(
        df,
        group=group,
        collision=collision,
        charge=charge,
        size=size,
        hull_offset=hull_offset,
        sticky=sticky,
        single_click_expand=single_click_expand,
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
html = build_elasticgraph_html(
    group, collision, charge, size, hull_offset, sticky, single_click_expand,
    show_side_panel, show_top_panel, dark_mode,
)
st.caption("Interactive elastic force-directed graph powered by D3Blocks and controlled by Streamlit.")
st.iframe(html, height=height, width="stretch")
