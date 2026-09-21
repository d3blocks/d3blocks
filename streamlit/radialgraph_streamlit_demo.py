"""
Minimal Streamlit demo: embed a d3blocks radialgraph chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run radialgraph_streamlit_demo.py

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
@st.cache_data
def load_data():
    d3 = D3Blocks()
    return d3.import_example("energy")

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - RadialGraph", layout="wide")
df = load_data()

# =============================================================================
# Sidebar — chart controls
# =============================================================================
st.sidebar.subheader("Layout")
center_options = ["(auto)"] + sorted(set(df["source"].astype(str).tolist() + df["target"].astype(str).tolist()))
center_choice = st.sidebar.selectbox("Center node", center_options, index=0)
center = None if center_choice == "(auto)" else center_choice

ring_spacing = st.sidebar.slider("Ring spacing", 40, 160, 70, 5)
auto_ring = st.sidebar.checkbox("Auto ring spacing", value=True)
radial_strength = st.sidebar.slider("Radial strength", 0.0, 1.0, 0.8, 0.05)
charge = st.sidebar.slider("Charge", -400, -20, -120, 10)

st.sidebar.subheader("Appearance")
color = st.sidebar.selectbox("Node color", ["cluster", "degree"], index=0)
size = st.sidebar.selectbox("Node size", ["degree", "cluster"], index=0)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)
show_bottom_panel = st.sidebar.checkbox("Show bottom node panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks radialgraph
# =============================================================================
@st.cache_data(show_spinner="Building radialgraph...")
def build_radialgraph_html(
    df,
    center,
    ring_spacing,
    auto_ring,
    radial_strength,
    charge,
    color,
    size,
    show_side_panel,
    show_top_panel,
    show_bottom_panel,
):
    d3 = D3Blocks()
    html = d3.radialgraph(
        df,
        center=center,
        ring_spacing=ring_spacing,
        auto_ring_spacing=auto_ring,
        radial_strength=radial_strength,
        charge=charge,
        color=color,
        size=size,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        show_bottom_panel=show_bottom_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_radialgraph_html(
    df,
    center,
    ring_spacing,
    auto_ring,
    radial_strength,
    charge,
    color,
    size,
    show_side_panel,
    show_top_panel,
    show_bottom_panel,
)
st.caption("Interactive radial network graph powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
