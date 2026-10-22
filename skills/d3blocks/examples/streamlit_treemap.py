"""Streamlit + treemap (value mode, panels, dark mode).

Requires: d3blocks streamlit
Run: streamlit run streamlit_treemap.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Treemap", layout="wide")
st.title("Treemap — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    value_mode = st.radio("Value mode", options=["size", "count"], horizontal=True)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    dark_mode = st.checkbox("Dark mode", value=False)
    height = st.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building treemap...")
def build_treemap_html(df, value_mode, show_side_panel, show_top_panel, dark_mode):
    d3 = D3Blocks()
    return d3.treemap(
        df,
        value=value_mode,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_treemap_html(df, value_mode, show_side_panel, show_top_panel, dark_mode)
st.caption("Nested rectangles sized by weight or count.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
