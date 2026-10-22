"""Streamlit + particles.

Requires: d3blocks streamlit
Run: streamlit run streamlit_particles.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Particles", layout="wide")
st.title("Particles — D3Blocks")

text = st.sidebar.text_input("Text", "D3Blocks")
shape = st.sidebar.selectbox("Shape", ["circle", "square"], index=0)
height = st.sidebar.slider("Chart height", 200, 800, 300, 50)

@st.cache_data(show_spinner="Building particles...")
def build(text, shape):
    return D3Blocks().particles(
        text,
        shape=shape,
        color_background="#000000",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build(text, shape)
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
