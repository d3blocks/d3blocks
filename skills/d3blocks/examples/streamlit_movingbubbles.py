"""Streamlit + movingbubbles (playback, colour method, size, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_movingbubbles.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Movingbubbles", layout="wide")
st.title("Movingbubbles — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example(
        "random_time",
        n=2000,
        c=50,
        date_start="1-1-2000 00:10:05",
        date_stop="1-1-2000 23:59:59",
    )

df = load_data()

st.sidebar.subheader("Playback")
damper = st.sidebar.slider("Damper", 0.1, 5.0, 1.0, 0.1)
fontsize = st.sidebar.slider("Font size", 8, 28, 14, 1)
timedelta = st.sidebar.selectbox("Timedelta", ["seconds", "minutes", "days"], index=1)

st.sidebar.subheader("Appearance")
color_method = st.sidebar.selectbox("Color method", ["state", "node"], index=0)
size = st.sidebar.slider("Bubble size", 2, 20, 5, 1)
opacity = st.sidebar.slider("Opacity", 0.1, 1.0, 0.6, 0.05)

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panel", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building movingbubbles...")
def build_movingbubbles_html(
    df,
    damper,
    fontsize,
    timedelta,
    color_method,
    size,
    opacity,
    show_side_panel,
    show_top_panel,
):
    d3 = D3Blocks()
    return d3.movingbubbles(
        df,
        damper=damper,
        fontsize=fontsize,
        timedelta=timedelta,
        color_method=color_method,
        size=size,
        opacity=opacity,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_movingbubbles_html(
    df,
    damper,
    fontsize,
    timedelta,
    color_method,
    size,
    opacity,
    show_side_panel,
    show_top_panel,
)
st.caption("Entities moving between states over time — playback and appearance in the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe missing (Streamlit < 1.56); using components.html")
    components.html(html, height=height, scrolling=False)
