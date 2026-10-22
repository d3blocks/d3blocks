"""Streamlit + tree (hierarchy levels, link length, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_tree.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Tree", layout="wide")
st.title("Tree — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

st.sidebar.subheader("Layout")
max_level = st.sidebar.slider("Max hierarchy level", 1, 8, 8, 1)
hierarchy = list(range(1, max_level + 1))
link_length = st.sidebar.slider("Link length", 80, 280, 180, 10)
font_size = st.sidebar.slider("Font size", 8, 20, 10, 1)

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panel", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building tree...")
def build_tree_html(df, hierarchy, link_length, font_size, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    return d3.tree(
        df,
        hierarchy=hierarchy,
        link_length=link_length,
        font={"size": font_size},
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_tree_html(df, hierarchy, link_length, font_size, show_side_panel, show_top_panel)
st.caption("Hierarchical tree from an energy edge list.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
