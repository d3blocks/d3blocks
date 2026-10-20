"""
Minimal Streamlit demo: embed a d3blocks ERD (entity-relationship diagram).

Run from a machine with d3blocks + streamlit installed:

    streamlit run erd_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch").
"""

import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Import your data here
# =============================================================================
DEFAULT_ERD = """erDiagram
    customers ||--o{ orders : places
    orders ||--|{ order_lines : contains
    products ||--o{ order_lines : "ordered as"
    orders |o..o| invoices : "billed by"
    customers {
        uuid id PK
        text email UK
        text name
    }
    orders {
        uuid id PK
        uuid customer_id FK
        timestamptz created_at
    }
    order_lines {
        uuid order_id PK,FK
        uuid product_id PK,FK
        int quantity
    }
    products {
        uuid id PK
        text sku UK
        numeric price
    }
"""

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - ERD", layout="wide")

# =============================================================================
# Sidebar — chart controls
# =============================================================================
st.sidebar.subheader("Diagram (Mermaid erDiagram)")
mermaid = st.sidebar.text_area("ER diagram", DEFAULT_ERD, height=300)

st.sidebar.subheader("Layout")
direction = st.sidebar.selectbox("Direction", ["LR", "TB", "RL", "BT"], index=0)
show_columns = st.sidebar.selectbox("Columns", ["all", "keys", "none"], index=0)
show_types = st.sidebar.checkbox("Column types", value=True)
nodesep = st.sidebar.slider("Node spacing", 10, 200, 50, 5)
ranksep = st.sidebar.slider("Rank spacing", 20, 300, 90, 5)

st.sidebar.subheader("Appearance")
dark_mode = st.sidebar.selectbox("Theme", ["light", "dark", "auto (follow OS)"], index=0)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)


# =============================================================================
# Build D3Blocks ERD
# =============================================================================
@st.cache_data(show_spinner="Building ERD...")
def build_erd_html(
    mermaid, direction, show_columns, show_types, nodesep, ranksep, dark_mode, show_side_panel, show_top_panel
):
    d3 = D3Blocks()
    html = d3.erd(
        mermaid,
        direction=direction,
        show_columns=show_columns,
        show_types=show_types,
        nodesep=nodesep,
        ranksep=ranksep,
        dark_mode={'light': False, 'dark': True}.get(dark_mode, 'auto'),
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        color_background="streamlit",
        filepath=None,
        showfig=False,
        return_html=True,
    )
    return html


# =============================================================================
# Main page
# =============================================================================
try:
    html = build_erd_html(
        mermaid, direction, show_columns, show_types, nodesep, ranksep, dark_mode, show_side_panel, show_top_panel
    )
except ValueError as e:
    st.error(str(e))
    st.stop()
st.caption("Interactive entity-relationship diagram powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
