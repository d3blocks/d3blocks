"""Streamlit + heatmap (fontsize, panels, dark mode).

Requires: d3blocks streamlit
Run: streamlit run streamlit_heatmap.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Heatmap", layout="wide")
st.title("Heatmap — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("stormofswords")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    fontsize = st.slider("Font size", 6, 20, 10, 1)
    dark_mode = st.checkbox("Dark mode", value=False)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    height = st.slider("Chart height", 400, 1200, 720, 20)

@st.cache_data(show_spinner="Building heatmap...")
def build_heatmap_html(df, fontsize, dark_mode, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    return d3.heatmap(
        df,
        fontsize=fontsize,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_heatmap_html(df, fontsize, dark_mode, show_side_panel, show_top_panel)
st.caption("Adjacency heatmap with clustering — Storm of Swords sample.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
