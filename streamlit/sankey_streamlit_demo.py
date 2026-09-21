"""
Minimal Streamlit demo: embed a d3blocks sankey chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run sankey_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch"). height="content" is unreliable when
  the chart uses position:fixed and contributes almost no document-flow height.
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
st.set_page_config(page_title="D3Blocks - Sankey Chart", layout="wide")
df = load_data()

# =============================================================================
# Sidebar — chart controls (match sankey side-panel options)
# =============================================================================
st.sidebar.subheader("Links")
link_color = st.sidebar.selectbox(
    "Link color",
    ["source-target", "source", "target"],
    index=0,
)
link_opacity = st.sidebar.slider("Link opacity", 0.1, 1.0, 0.5, 0.05)

st.sidebar.subheader("Nodes")
node_align = st.sidebar.selectbox(
    "Align",
    ["justify", "left", "right", "center"],
    index=0,
)
node_width = st.sidebar.slider("Node width", 5, 40, 15, 1)
node_padding = st.sidebar.slider("Node padding", 5, 40, 15, 1)
fontsize = st.sidebar.slider("Font size", 6, 24, 10, 1)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks sankey
# =============================================================================
@st.cache_data(show_spinner="Building sankey...")
def build_sankey_html(
    df,
    link_color,
    link_opacity,
    node_align,
    node_width,
    node_padding,
    fontsize,
    show_side_panel,
    show_top_panel,
):
    d3 = D3Blocks()
    html = d3.sankey(
        df,
        link={
            "color": link_color,
            "stroke_opacity": link_opacity,
            "color_static": "#d3d3d3",
        },
        node={
            "align": node_align,
            "width": node_width,
            "padding": node_padding,
            "color": "currentColor",
        },
        fontsize=fontsize,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_sankey_html(
    df,
    link_color,
    link_opacity,
    node_align,
    node_width,
    node_padding,
    fontsize,
    show_side_panel,
    show_top_panel,
)
st.caption("Interactive sankey diagram powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
