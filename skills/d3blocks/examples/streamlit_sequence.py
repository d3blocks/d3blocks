"""Streamlit + sequence (requires D3Blocks.sequence).

Requires: d3blocks streamlit with sequence support
Run: streamlit run streamlit_sequence.py
"""
import pandas as pd
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Sequence", layout="wide")
st.title("Sequence — D3Blocks")

d3 = D3Blocks()
if not hasattr(d3, "sequence"):
    st.error("Installed d3blocks has no D3Blocks.sequence method.")
    st.stop()

df = pd.DataFrame(
    {
        "source": ["Alice", "Bob", "Alice"],
        "target": ["Bob", "Alice", "Bob"],
        "label": ["Hello", "Hi!", "OK"],
        "style": ["sync", "reply", "sync"],
    }
)
height = st.sidebar.slider("Chart height", 400, 1200, 500, 50)

@st.cache_data(show_spinner="Building sequence...")
def build(df):
    return D3Blocks().sequence(
        df,
        showfig=False,
        return_html=True,
        filepath=None,
        color_background="streamlit",
        dark_mode=False,
    )

html = build(df)
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
