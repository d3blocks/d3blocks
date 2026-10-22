"""Streamlit + violin (bins, jitter, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_violin.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Violin", layout="wide")
st.title("Violin — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("cancer")

df = load_data()

with st.sidebar:
    st.header("Chart settings")
    bins = st.slider("Bins", 5, 80, 50, 1)
    jitter = st.slider("Jitter", 0, 80, 40, 1)
    dark_mode = st.checkbox("Dark mode", value=False)
    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)
    height = st.slider("Chart height", 400, 1200, 700, 50)

x_order = ["acc", "kich", "brca", "lgg", "blca", "coad", "ov"]
tooltip = (
    df["labx"].astype(str).values
    + " <br /> Survival: "
    + df["survival_months"].astype(str).values
)

@st.cache_data(show_spinner="Building violin...")
def build_violin_html(df, bins, jitter, dark_mode, show_side_panel, show_top_panel, tooltip):
    d3 = D3Blocks()
    return d3.violin(
        x=df["labx"].values,
        y=df["age"].values,
        size=df["survival_months"].values / 10,
        tooltip=tooltip,
        bins=bins,
        jitter=jitter,
        x_order=x_order,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=dark_mode,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
        figsize=[900, None],
    )

html = build_violin_html(
    df, bins, jitter, dark_mode, show_side_panel, show_top_panel, tooltip
)
st.caption("Age distributions by cancer type — bins and jitter in the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
