"""
Minimal Streamlit demo: embed a d3blocks sequence diagram.

Run from a machine with d3blocks + streamlit installed:

    streamlit run sequence_streamlit_demo.py

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
DEFAULT_SEQUENCE = """sequenceDiagram
    actor User
    participant Web as Web App
    participant API
    participant Auth
    participant DB as Postgres
    rect rgb(224, 242, 254)
        User->>Web: open dashboard
        Web->>API: GET /dashboard
        API->>Auth: verify JWT
        Auth-->>API: claims ok
    end
    rect rgb(220, 252, 231)
        API->>DB: query profile + metrics
        DB-->>API: rows
    end
    API-->>Web: 200 JSON
    Web-->>User: render
"""

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - Sequence", layout="wide")

# =============================================================================
# Sidebar — chart controls
# =============================================================================
st.sidebar.subheader("Diagram (Mermaid sequenceDiagram)")
mermaid = st.sidebar.text_area("Sequence diagram", DEFAULT_SEQUENCE, height=300)

st.sidebar.subheader("Layout")
message_spacing = st.sidebar.slider("Message spacing", 24, 120, 44, 2)
wrap = st.sidebar.slider("Wrap labels at (characters)", 10, 80, 28, 1)
font_size = st.sidebar.slider("Font size", 8, 24, 13, 1)

st.sidebar.subheader("Appearance")
dark_mode = st.sidebar.selectbox(
    "Theme", ["light", "dark", "auto (follow OS)"], index=0
)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider(
    "Chart height", min_value=400, max_value=1200, value=700, step=50
)


# =============================================================================
# Build D3Blocks sequence diagram
# =============================================================================
@st.cache_data(show_spinner="Building sequence diagram...")
def build_sequence_html(
    mermaid,
    message_spacing,
    wrap,
    font_size,
    dark_mode,
    show_side_panel,
    show_top_panel,
):
    d3 = D3Blocks()
    html = d3.sequence(
        mermaid,
        message_spacing=message_spacing,
        wrap=wrap,
        font={"size": font_size},
        dark_mode={"light": False, "dark": True}.get(dark_mode, "auto"),
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
    html = build_sequence_html(
        mermaid,
        message_spacing,
        wrap,
        font_size,
        dark_mode,
        show_side_panel,
        show_top_panel,
    )
except ValueError as e:
    st.error(str(e))
    st.stop()
st.caption(
    "Interactive sequence diagram powered by D3Blocks and controlled by Streamlit. "
    "Use ▶ Walk through to step through the messages."
)
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning(
        "st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html."
    )
    components.html(html, height=height, scrolling=False)
