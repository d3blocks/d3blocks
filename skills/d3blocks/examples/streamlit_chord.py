"""Streamlit + advanced chord (ordering, font, dark mode, panel toggles).

Requires: pip install d3blocks streamlit
Run: streamlit run streamlit_chord.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Chord", layout="wide")
st.title("Chord — D3Blocks")

with st.sidebar:
    st.header("Chart settings")
    ordering = st.radio(
        "Ordering",
        options=["ascending", "descending", ""],
        format_func=lambda x: x or "none",
        horizontal=True,
    )
    color_mode = st.selectbox(
        "Link color",
        options=["source", "target", "source-target"],
        index=0,
    )
    fontsize = st.slider("Font size", 6, 24, 11, 1)
    margin = st.slider("Margin (label space)", 80, 320, 180, 10)
    dark_mode = st.checkbox("Dark mode", value=False)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")
    height = st.slider("Chart height", 400, 1200, 800, 50)

@st.cache_data(show_spinner="Building chord...")
def build_chord_html(ordering, color_mode, fontsize, margin, dark_mode, show_side_panel, show_top_panel):
    d3 = D3Blocks()
    df = d3.import_example("energy")
    return d3.chord(
        df,
        color=color_mode,
        opacity="source",
        ordering=ordering,
        fontsize=fontsize,
        margin=margin,
        text_offset=10,
        figsize=[900, 900],
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_chord_html(
    ordering, color_mode, fontsize, margin, dark_mode, show_side_panel, show_top_panel
)
st.caption("Energy flow chord — ordering, colour mode, and margins from the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
