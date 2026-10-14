"""
Minimal Streamlit demo: embed a d3blocks flowgraph chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run flowgraph_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch").
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Import your data here
# =============================================================================
DEFAULT_FLOW = """flowchart LR
    start([Order received]) --> check{In stock?}
    check -->|yes| pick[Pick & pack]
    check -->|no| back[[Backorder]] -.->|restocked| check
    subgraph wh [Warehouse]
        pick --> ship[/Ship parcel/]
        pick --> inspect((Inspect))
    end
    ship ==> done([Delivered])
    ship --> db[(Orders DB)]
"""

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - Flowgraph", layout="wide")

# =============================================================================
# Sidebar — chart controls
# =============================================================================
st.sidebar.subheader("Diagram (Mermaid flowchart)")
mermaid = st.sidebar.text_area("Flowchart", DEFAULT_FLOW, height=260)

st.sidebar.subheader("Layout")
layout = st.sidebar.selectbox("Layout engine", ["dagre", "elk"], index=0)
direction = st.sidebar.selectbox("Direction", ["LR", "TB", "RL", "BT"], index=0)
nodesep = st.sidebar.slider("Node spacing", 10, 150, 40, 5)
ranksep = st.sidebar.slider("Rank spacing", 20, 250, 70, 5)
curve = st.sidebar.selectbox("Edges", ["smooth", "straight"], index=0)

st.sidebar.subheader("Appearance")
animate = st.sidebar.selectbox("Animation", ["none", "pulse", "dash", "dots", "comet"], index=0)
show_groups = st.sidebar.checkbox("Groups", value=True)
show_edge_labels = st.sidebar.checkbox("Edge labels", value=True)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks flowgraph
# =============================================================================
@st.cache_data(show_spinner="Building flowgraph...")
def build_flowgraph_html(
    mermaid,
    layout,
    direction,
    nodesep,
    ranksep,
    curve,
    animate,
    show_groups,
    show_edge_labels,
    show_side_panel,
    show_top_panel,
):
    d3 = D3Blocks()
    html = d3.flowgraph(
        mermaid,
        layout=layout,
        direction=direction,
        nodesep=nodesep,
        ranksep=ranksep,
        curve=curve,
        animate=animate,
        show_groups=show_groups,
        show_edge_labels=show_edge_labels,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        filepath=None,
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_flowgraph_html(
    mermaid,
    layout,
    direction,
    nodesep,
    ranksep,
    curve,
    animate,
    show_groups,
    show_edge_labels,
    show_side_panel,
    show_top_panel,
)
st.caption("Interactive process flow powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
