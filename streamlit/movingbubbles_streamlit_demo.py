"""
Minimal Streamlit demo: embed a d3blocks movingbubbles chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run movingbubbles_streamlit_demo.py

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
    return d3.import_example(
        "random_time",
        n=2000,
        c=50,
        date_start="1-1-2000 00:10:05",
        date_stop="1-1-2000 23:59:59",
    )

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - Movingbubbles", layout="wide")
df = load_data()

# =============================================================================
# Sidebar — chart controls
# =============================================================================
st.sidebar.subheader("Playback")
damper = st.sidebar.slider("Damper", 0.1, 5.0, 1.0, 0.1)
fontsize = st.sidebar.slider("Font size", 8, 28, 14, 1)
timedelta = st.sidebar.selectbox("Timedelta", ["seconds", "minutes", "days"], index=1)

st.sidebar.subheader("Appearance")
color_method = st.sidebar.selectbox("Color method", ["state", "node"], index=0)
size = st.sidebar.slider("Bubble size", 2, 20, 5, 1)
opacity = st.sidebar.slider("Opacity", 0.1, 1.0, 0.6, 0.05)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks movingbubbles
# =============================================================================
@st.cache_data(show_spinner="Building movingbubbles...")
def build_movingbubbles_html(
    df,
    damper,
    fontsize,
    timedelta,
    color_method,
    size,
    opacity,
    show_side_panel,
    show_top_panel,
):
    d3 = D3Blocks()
    html = d3.movingbubbles(
        df,
        damper=damper,
        fontsize=fontsize,
        timedelta=timedelta,
        color_method=color_method,
        size=size,
        opacity=opacity,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_movingbubbles_html(
    df,
    damper,
    fontsize,
    timedelta,
    color_method,
    size,
    opacity,
    show_side_panel,
    show_top_panel,
)
st.caption("Interactive moving bubbles powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
