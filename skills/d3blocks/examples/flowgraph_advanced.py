"""Advanced flowgraph: shapes, edge variants, groups, Mermaid + ELK, state diagram.

Requires: pip install d3blocks
Run: python flowgraph_advanced.py
"""
import pandas as pd
from d3blocks import D3Blocks

# --- 1) Edge list with shapes, labels, variants, then edit + redraw ---
d3 = D3Blocks(frame=False)

edges = pd.DataFrame({
    "source": ["Start", "Valid?", "Valid?", "Fix", "Valid?", "Ship"],
    "target": ["Valid?", "Ship", "Fix", "Valid?", "Done", "Done"],
    "label": ["", "ok", "no", "retry", "", ""],
    "variant": ["default", "emphasis", "error", "async", "default", "default"],
})
nodes = {
    "Start": {"label": "Start", "shape": "terminal", "group": "intake"},
    "Valid?": {"label": "Valid?", "shape": "decision", "group": "intake"},
    "Fix": {"label": "Fix input", "shape": "process", "group": "intake"},
    "Ship": {"label": "Ship", "shape": "process", "group": "outbound"},
    "Done": {"label": "Done", "shape": "terminal", "group": "outbound"},
}
groups = {
    "intake": {"label": "Intake", "color": "#4e79a7"},
    "outbound": {"label": "Outbound", "color": "#59a14f"},
}

d3.flowgraph(
    edges,
    nodes=nodes,
    groups=groups,
    direction="TB",
    layout="dagre",
    show_edge_labels=True,
    show_groups=True,
    animate=False,
    filepath="flowgraph_process.html",
    title="Order process",
    dark_mode=True,
)

d3.node_properties["Fix"]["color"] = "#e15759"
d3.edge_properties.loc[0, "label"] = "begin"
d3.show(filepath="flowgraph_process_edited.html")

# --- 2) Mermaid architecture diagram with subgraphs (ELK layout) ---
d3.flowgraph(
    """
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
""",
    layout="elk",
    direction="LR",
    filepath="flowgraph_api_elk.html",
    title="API architecture (ELK)",
    dark_mode="auto",
)

# --- 3) Group-to-node links from a DataFrame ---
edges_g = pd.DataFrame({"source": ["Workers", "Workers"], "target": ["PG", "Cache"]})
nodes_g = {
    "W1": {"group": "Workers", "label": "scheduler"},
    "W2": {"group": "Workers", "label": "sync"},
    "PG": {"shape": "database", "label": "PostgreSQL"},
    "Cache": {"shape": "database", "label": "Redis"},
}
d3.flowgraph(
    edges_g,
    nodes=nodes_g,
    groups={"Workers": {"label": "Background workers"}},
    direction="LR",
    filepath="flowgraph_group_links.html",
    title="Workers to stores",
)

# --- 4) State diagram (Mermaid) ---
d3.flowgraph(
    """
stateDiagram-v2
    [*] --> pending : created
    pending --> done : ok
    pending --> failed : error
    done --> [*]
    failed --> pending : retry
    failed --> [*]
    note right of pending
        Waits for review
    end note
""",
    filepath="flowgraph_state.html",
    title="Ticket lifecycle",
    dark_mode=True,
)
