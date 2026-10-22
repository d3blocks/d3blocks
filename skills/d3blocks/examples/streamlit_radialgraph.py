"""Streamlit + radialgraph (center, rings, force, appearance, panels).

Requires: d3blocks streamlit
Run: streamlit run streamlit_radialgraph.py
"""
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(page_title="D3Blocks — RadialGraph", layout="wide")
st.title("RadialGraph — D3Blocks")

@st.cache_data
def load_data():
    return D3Blocks().import_example("energy")

df = load_data()

st.sidebar.subheader("Layout")
node_names = sorted(
    set(df["source"].astype(str).tolist() + df["target"].astype(str).tolist())
)
center_choice = st.sidebar.selectbox("Center node", ["(auto)"] + node_names, index=0)
center = None if center_choice == "(auto)" else center_choice

ring_spacing = st.sidebar.slider("Ring spacing", 40, 160, 70, 5)
auto_ring = st.sidebar.checkbox("Auto ring spacing", value=True)
radial_strength = st.sidebar.slider("Radial strength", 0.0, 1.0, 0.8, 0.05)
charge = st.sidebar.slider("Charge", -400, -20, -120, 10)

st.sidebar.subheader("Appearance")
color = st.sidebar.selectbox("Node color", ["cluster", "degree"], index=0)
size = st.sidebar.selectbox("Node size", ["degree", "cluster"], index=0)

st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show side panel", value=False)
show_top_panel = st.sidebar.checkbox("Show top panel", value=True)
show_bottom_panel = st.sidebar.checkbox("Show bottom node panel", value=True)

st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

@st.cache_data(show_spinner="Building radialgraph...")
def build_radialgraph_html(
    df,
    center,
    ring_spacing,
    auto_ring,
    radial_strength,
    charge,
    color,
    size,
    show_side_panel,
    show_top_panel,
    show_bottom_panel,
):
    d3 = D3Blocks()
    return d3.radialgraph(
        df,
        center=center,
        ring_spacing=ring_spacing,
        auto_ring_spacing=auto_ring,
        radial_strength=radial_strength,
        charge=charge,
        color=color,
        size=size,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        show_bottom_panel=show_bottom_panel,
        dark_mode=False,
        color_background="streamlit",
        showfig=False,
        return_html=True,
        filepath=None,
    )

html = build_radialgraph_html(
    df,
    center,
    ring_spacing,
    auto_ring,
    radial_strength,
    charge,
    color,
    size,
    show_side_panel,
    show_top_panel,
    show_bottom_panel,
)
st.caption("Radial network by hop-distance from a focus — controls in the sidebar.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe missing (Streamlit < 1.56); using components.html")
    components.html(html, height=height, scrolling=False)
