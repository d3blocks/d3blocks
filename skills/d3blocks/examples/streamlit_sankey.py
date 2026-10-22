"""Streamlit + sankey (link colour/opacity, node align/size, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_sankey.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Sankey", layout="wide")
st.title("Sankey — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

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

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panel", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

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
    return d3.sankey(
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
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

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
st.caption("Stage-to-stage flows — link and node options in the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe missing (Streamlit < 1.56); using components.html")
    components.html(html, height=height, scrolling=False)
