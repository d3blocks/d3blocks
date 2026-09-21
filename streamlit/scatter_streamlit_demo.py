"""
Minimal Streamlit demo: embed a d3blocks scatter chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run scatter_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch"). height="content" is unreliable because the
  scatter uses position:fixed and contributes almost no document-flow height.
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Import your data here
# =============================================================================
@st.cache_data
def load_data():
    d3 = D3Blocks(chart="Scatter")
    return d3.import_example("cancer")

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - Scatter Chart", layout="wide")
# load Data
df = load_data()

# =============================================================================
# Sidebar
# =============================================================================
# Point appearance
st.sidebar.subheader("Points")
size_variable = st.sidebar.selectbox("Size", ["survival_months", "constant"], index=0)

if size_variable == "survival_months":
    size_scale = st.sidebar.slider("Size scale", 1, 50, 10, 1)
    size = df["survival_months"].fillna(1).clip(lower=1) / size_scale
else:
    size = 5

# Color
st.sidebar.subheader("Color")
color_variable = st.sidebar.selectbox("Color by", ["labx", "white"], index=0)
if color_variable == "labx":
    color = df["labx"].fillna("Unknown")
else:
    color = "#ffffff"

# Tooltip
st.sidebar.subheader("Tooltip")
show_cancer   = st.sidebar.checkbox("Cancer type", True)
show_survival = st.sidebar.checkbox("Survival", True)
show_age      = st.sidebar.checkbox("Age", False)

# Build tooltip
tooltip = []
for _, row in df.iterrows():
    parts = []
    if show_cancer:   parts.append(f"Cancer: {row['labx']}")
    if show_survival: parts.append(f"Survival: {row['survival_months']}")
    if show_age:      parts.append(f"Age: {row['age']}")
    tooltip.append("<br>".join(parts))

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False,)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks scatter
# =============================================================================
@st.cache_data(show_spinner="Building scatter...")
def build_scatter_html(size, color, tooltip, df, show_side_panel, show_top_panel):

    # Initialize
    d3 = D3Blocks(chart="Scatter")
    # Create html
    html = d3.scatter(
        x=df['tsneX'].values,
        y=df['tsneY'].values,
        x1=df['PC1'].values,
        y1=df['PC2'].values,
        size=size,
        color=color,
        opacity=0.3,
        tooltip=tooltip,
        scale=True,
        label_radio=['tSNE','PCA'],
        df=df,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background='streamlit',
        showfig=False,
        return_html=True,
    )

    # Return html
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_scatter_html(size, color, tooltip, df, show_side_panel, show_top_panel)
st.caption("Interactive scatter plot powered by D3Blocks and controlled by Streamlit.")
st.iframe(html, height=height, width="stretch")
