"""Minimal Streamlit demo for d3blocks Violin.

Run: streamlit run violin_streamlit_demo.py
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="Violin – D3Blocks", layout="wide")
st.title("Violin – D3Blocks")

# =============================================================================
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.header("Chart settings")
    bins = st.slider("Bins", min_value=5, max_value=80, value=50, step=1)
    jitter = st.slider("Jitter", min_value=0, max_value=80, value=40, step=1)
    dark_mode = st.checkbox("Dark mode", value=False)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=True)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")
    height = st.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build chart
# =============================================================================
d3 = D3Blocks()
df = d3.import_example("cancer")
tooltip = df["labx"].values + " <br /> Survival: " + df["survival_months"].astype(str).values
html = d3.violin(
    x=df["labx"].values,
    y=df["age"].values,
    size=df["survival_months"].values / 10,
    tooltip=tooltip,
    bins=bins,
    jitter=jitter,
    x_order=["acc", "kich", "brca", "lgg", "blca", "coad", "ov"],
    show_side_panel=show_side_panel,
    show_top_panel=show_top_panel,
    dark_mode=dark_mode,
    color_background="streamlit",
    showfig=False,
    return_html=True,
    filepath=None,
    figsize=[900, None],
)

# =============================================================================
# Display chart
# =============================================================================
st.iframe(html, height=height)
