"""Streamlit + elasticgraph (charge, collision, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_elasticgraph.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Elasticgraph", layout="wide")
st.title("Elasticgraph — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    charge = st.slider("Charge", 100, 1000, 500, 50)
    collision = st.slider("Collision", 0.1, 2.0, 0.5, 0.1)
    dark_mode = st.checkbox("Dark mode", value=False)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    height = st.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building elasticgraph...")
def build_elasticgraph_html(df, charge, collision, dark_mode, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    return d3.elasticgraph(
        df,
        charge=charge,
        collision=collision,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_elasticgraph_html(df, charge, collision, dark_mode, show_side_panel, show_top_panel)
st.caption("Clustered force-directed network.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
