"""Streamlit + matrix.

Requires: d3blocks streamlit
Run: streamlit run streamlit_matrix.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Matrix", layout="wide")
st.title("Matrix — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()
with st.sidebar:
    scale = st.checkbox("Scale", value=False)
    height = st.slider("Chart height", 400, 1200, 600, 50)

@st.cache_data(show_spinner="Building matrix...")
def build(df, scale):
    return D3Blocks().matrix(
        df,
        scale=scale,
        showfig=False,
        return_html=True,
        filepath=None,
        color_background="streamlit",
    )

html = build(df, scale)
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
