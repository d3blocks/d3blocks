"""Streamlit + imageslider.

Requires: d3blocks streamlit (network for internet sample)
Run: streamlit run streamlit_imageslider.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Imageslider", layout="wide")
st.title("Imageslider — D3Blocks")

example = st.sidebar.selectbox(
    "Example",
    ["southern_nebula_internet", "southern_nebula"],
    index=0,
)
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building imageslider...")
def build(example):
    d3 = D3Blocks()
    before, after = d3.import_example(example)
    return d3.imageslider(
        before,
        after,
        showfig=False,
        return_html=True,
        color_background="streamlit",
    )

html = build(example)
st.caption("Before / after comparison.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
