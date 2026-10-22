"""Streamlit + erd (requires D3Blocks.erd).

Requires: d3blocks streamlit with erd support
Run: streamlit run streamlit_erd.py
"""
import pandas as pd
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — ERD", layout="wide")
st.title("ERD — D3Blocks")

d3 = D3Blocks()
if not hasattr(d3, "erd"):
    st.error("Installed d3blocks has no D3Blocks.erd method.")
    st.stop()

df = pd.DataFrame(
    {
        "source": ["Customer", "Order"],
        "target": ["Order", "LineItem"],
        "source_card": ["one", "one"],
        "target_card": ["zero_or_more", "one_or_more"],
    }
)
height = st.sidebar.slider("Chart height", 400, 1200, 500, 50)

@st.cache_data(show_spinner="Building erd...")
def build(df):
    return D3Blocks().erd(
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
