"""Streamlit + circlepacking (size, zoom, border, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_circlepacking.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Circlepacking", layout="wide")
st.title("Circlepacking — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

st.sidebar.subheader("Layout")
size = st.sidebar.selectbox("Node size", ["sum", "constant"], index=0)
zoom = st.sidebar.selectbox("Zoom trigger", ["click", "mouseover"], index=0)
speed = st.sidebar.slider("Zoom speed (ms)", 100, 2500, 750, 50)
padding = st.sidebar.slider("Padding", 0, 40, 5, 1)
font_size = st.sidebar.slider("Font size", 8, 48, 20, 1)
border_width = st.sidebar.slider("Border width", 0.0, 6.0, 1.5, 0.5)

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panels", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)
dark_mode = st.sidebar.checkbox("Dark mode", value=False)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building circlepacking...")
def build_circlepacking_html(
    size, zoom, speed, padding, font_size, border_width, show_side_panel, show_top_panel, dark_mode
):
    d3 = D3Blocks()
    return d3.circlepacking(
        df,
        size=size,
        zoom=zoom,
        speed=speed,
        border={"color": "#FFFFFF", "width": border_width, "fill": "#FFFFFF", "padding": padding},
        font={"size": font_size, "type": "sans-serif"},
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_circlepacking_html(
    size, zoom, speed, padding, font_size, border_width, show_side_panel, show_top_panel, dark_mode
)
st.caption("Nested circles from an energy hierarchy.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
