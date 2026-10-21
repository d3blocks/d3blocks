"""Streamlit + advanced scatter (tSNE/PCA, size/color/tooltip, panel toggles).

Requires: pip install d3blocks streamlit
Run: streamlit run streamlit_scatter.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Scatter", layout="wide")
st.title("Scatter — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks(chart="Scatter").import_example("cancer")

df = load_data()

st.sidebar.subheader("Points")
size_mode = st.sidebar.selectbox("Size by", ["survival_months", "constant"], index=0)
if size_mode == "survival_months":
    size_scale = st.sidebar.slider("Size scale", 1, 50, 10, 1)
    size = df["survival_months"].fillna(1).clip(lower=1) / size_scale
else:
    size = 5

st.sidebar.subheader("Color")
color_mode = st.sidebar.selectbox("Color by", ["labx", "fixed white"], index=0)
color = df["labx"].fillna("Unknown") if color_mode == "labx" else "#ffffff"

st.sidebar.subheader("Tooltip fields")
show_cancer = st.sidebar.checkbox("Cancer type", True)
show_survival = st.sidebar.checkbox("Survival", True)
show_age = st.sidebar.checkbox("Age", False)

tooltip = []
for _, row in df.iterrows():
    parts = []
    if show_cancer:
        parts.append(f"Cancer: {row['labx']}")
    if show_survival:
        parts.append(f"Survival: {row['survival_months']}")
    if show_age:
        parts.append(f"Age: {row['age']}")
    tooltip.append("<br>".join(parts) if parts else "")

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panel", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building scatter...")
def build_scatter_html(size, color, tooltip, df, show_side_panel, show_top_panel):
    d3 = D3Blocks(chart="Scatter")
    return d3.scatter(
        x=df["tsneX"].values,
        y=df["tsneY"].values,
        x1=df["PC1"].values,
        y1=df["PC2"].values,
        size=size,
        color=color,
        opacity=0.35,
        tooltip=tooltip,
        scale=True,
        label_radio=["tSNE", "PCA"],
        df=df,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_scatter_html(size, color, tooltip, df, show_side_panel, show_top_panel)
st.caption("t-SNE / PCA with size, color, and tooltips — controlled from the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe missing (Streamlit < 1.56); using components.html")
    components.html(html, height=height, scrolling=False)
