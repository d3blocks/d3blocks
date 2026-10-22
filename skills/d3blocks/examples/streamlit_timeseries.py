"""Streamlit + timeseries (fontsize, panels, dark mode).

Requires: d3blocks streamlit
Run: streamlit run streamlit_timeseries.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Timeseries", layout="wide")
st.title("Timeseries — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("climate")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    dark_mode = st.checkbox("Dark mode", value=False)
    fontsize = st.slider("Font size", 8, 24, 10, 1)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    height = st.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building timeseries...")
def build_timeseries_html(df, fontsize, dark_mode, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    return d3.timeseries(
        df,
        datetime="date",
        dt_format="%Y-%m-%d",
        fontsize=fontsize,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_timeseries_html(df, fontsize, dark_mode, show_side_panel, show_top_panel)
st.caption("Climate series over time.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
