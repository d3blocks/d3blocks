"""Streamlit + maps (overseas, panels, dark mode).

Requires: d3blocks streamlit
Run: streamlit run streamlit_maps.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Maps", layout="wide")
st.title("Maps — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("surfspots")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    dark_mode = st.checkbox("Dark mode", value=False)
    include_overseas = st.checkbox("Include overseas", value=False)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    height = st.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building maps...")
def build_maps_html(df, include_overseas, dark_mode, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    return d3.maps(
        df,
        include_overseas=include_overseas,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_maps_html(df, include_overseas, dark_mode, show_side_panel, show_top_panel)
st.caption("Surf spots on a world map.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
