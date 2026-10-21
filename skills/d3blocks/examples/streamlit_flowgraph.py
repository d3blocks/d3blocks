"""Streamlit + advanced flowgraph (direction, layout, Mermaid vs edges, panels).

Requires: pip install d3blocks streamlit
Run: streamlit run streamlit_flowgraph.py
"""
import pandas as pd
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — Flowgraph", layout="wide")
st.title("Flowgraph — D3Blocks")

with st.sidebar:
    st.header("Chart settings")
    source = st.radio("Input", ["Edge list", "Mermaid architecture"], index=0)
    direction = st.selectbox("Direction", ["TB", "LR", "RL", "BT"], index=0)
    layout = st.selectbox("Layout engine", ["dagre", "elk"], index=0)
    show_groups = st.checkbox("Show groups", value=True)
    show_edge_labels = st.checkbox("Show edge labels", value=True)

    st.subheader("D3Blocks UI")
    show_side_panel = st.checkbox("Show side panel", value=False)
    show_top_panel = st.checkbox("Show top panel", value=True)

    st.subheader("Display")
    height = st.slider("Chart height", 400, 1200, 700, 50)

EDGES = pd.DataFrame({
    "source": ["Start", "Valid?", "Valid?", "Fix", "Valid?"],
    "target": ["Valid?", "Ship", "Fix", "Valid?", "Done"],
    "label": ["", "ok", "no", "retry", ""],
    "variant": ["default", "emphasis", "error", "async", "default"],
})
NODES = {
    "Start": {"label": "Start", "shape": "terminal", "group": "intake"},
    "Valid?": {"label": "Valid?", "shape": "decision", "group": "intake"},
    "Fix": {"label": "Fix input", "shape": "process", "group": "intake"},
    "Ship": {"label": "Ship", "shape": "process", "group": "outbound"},
    "Done": {"label": "Done", "shape": "terminal", "group": "outbound"},
}
GROUPS = {
    "intake": {"label": "Intake"},
    "outbound": {"label": "Outbound"},
}

MERMAID = """
flowchart LR
  subgraph api [API]
    gw[Gateway] --> svc[Orders]
  end
  subgraph data [Data]
    db[(Postgres)]
    q[[Worker queue]]
  end
  svc --> db
  svc -.->|events| q
  clients([Clients]) ==> gw
"""

@st.cache_data(show_spinner="Building flowgraph...")
def build_flowgraph_html(
    source, direction, layout, show_groups, show_edge_labels, show_side_panel, show_top_panel
):
    d3 = D3Blocks(frame=False)
    if source == "Mermaid architecture":
        return d3.flowgraph(
            MERMAID,
            layout=layout,
            direction=direction if direction else None,
            show_groups=show_groups,
            show_edge_labels=show_edge_labels,
            show_side_panel=show_side_panel,
            show_top_panel=show_top_panel,
            dark_mode=False,
            color_background="streamlit",
            showfig=False,
            return_html=True,
            filepath=None,
        )
    return d3.flowgraph(
        EDGES,
        nodes=NODES,
        groups=GROUPS,
        direction=direction,
        layout=layout,
        show_groups=show_groups,
        show_edge_labels=show_edge_labels,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_flowgraph_html(
    source, direction, layout, show_groups, show_edge_labels, show_side_panel, show_top_panel
)
st.caption("Process edge list or Mermaid architecture — layout and direction from the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    components.html(html, height=height, scrolling=False)
