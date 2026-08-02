"""Smoke tests for the RadialGraph block (force-directed, Obsidian-style)."""
import re
import pandas as pd
from d3blocks import D3Blocks


def _sample_df():
    # A many-to-many graph with a cycle (D->A->E->D) - not tree-shaped,
    # which is exactly the point: this block must not require a tree.
    return pd.DataFrame({
        'source': ['D', 'D', 'D', 'A', 'A', 'B', 'B', 'A'],
        'target': ['A', 'B', 'C', 'A1', 'A2', 'B1', 'B2', 'E'],
        'weight': [1, 1, 1, 1, 1, 1, 1, 1],
    })


def test_radialgraph_delegates_to_d3graph():
    """Node/edge styling should come from real d3graph computation, not
    static per-node defaults - e.g. edge width must vary with edge weight.
    """
    d3 = D3Blocks(chart='radialgraph', frame=False)
    df = pd.DataFrame({
        'source': ['root', 'root', 'A', 'A'],
        'target': ['A', 'B', 'A1', 'A2'],
        'weight': [10, 1, 5, 5],
    })
    html = d3.radialgraph(df, showfig=False, return_html=True)
    assert '"link_width"' in html
    # A heavier edge (weight=10) must render wider than a lighter one (weight=1).
    widths = [float(w) for w in re.findall(r'"link_width":\s*([0-9.]+)', html)]
    assert max(widths) > min(widths)


def test_radialgraph_returns_html():
    d3 = D3Blocks(chart='radialgraph', frame=False)
    html = d3.radialgraph(_sample_df(), showfig=False, return_html=True)
    assert isinstance(html, str)
    assert 'radialgraph-container' in html
    assert 'd3.forceSimulation' in html


def test_radialgraph_handles_cycles_and_many_to_many():
    """The old tree-based version silently discarded any edge giving a
    node a second parent. This must not happen anymore: every edge in the
    input should appear in the rendered link list.
    """
    d3 = D3Blocks(chart='radialgraph', frame=False)
    df = _sample_df()
    html = d3.radialgraph(df, showfig=False, return_html=True)
    link_count = html.count('"link_color"')
    assert link_count == len(df)


def test_radialgraph_node_properties_editable():
    d3 = D3Blocks(chart='radialgraph', frame=False)
    df = _sample_df()
    d3.set_node_properties(df)
    d3.node_properties.get('A')['color'] = '#000000'
    d3.node_properties.get('A')['size'] = 20
    d3.set_edge_properties(df)
    html = d3.show(return_html=True, showfig=False)
    assert '#000000' in html


def test_radialgraph_has_scroll_zoom_and_drag():
    d3 = D3Blocks(chart='radialgraph', frame=False)
    html = d3.radialgraph(_sample_df(), showfig=False, return_html=True)
    assert 'd3.zoom()' in html
    assert 'dblclick.zoom' in html
    assert 'd3.drag()' in html


def test_radialgraph_local_mode_computes_depth_rings():
    """center=<node> should switch on the radial force and give every
    reachable node a numeric BFS depth (used as its ring radius).
    """
    d3 = D3Blocks(chart='radialgraph', frame=False)
    html = d3.radialgraph(_sample_df(), center='D', showfig=False, return_html=True)
    assert '"center": "D"' in html
    assert 'forceRadial' in html
    depths = [int(d) for d in re.findall(r'"depth":\s*(\d+)', html)]
    assert max(depths) >= 2  # D(0) -> A(1) -> A1(2), at least 3 rings deep
    assert min(depths) == 0  # D itself


def test_radialgraph_no_center_autopicks_highest_degree():
    """center=None (the default) auto-picks the highest-degree node as
    focus and stays in local/ring mode - it does NOT fall back to a
    center-less global mode. This is a deliberate design choice (see
    RadialGraph.py's set_node_properties docstring), not the old
    behavior a previous test version assumed.
    """
    d3 = D3Blocks(chart='radialgraph', frame=False)
    html = d3.radialgraph(_sample_df(), center=None, showfig=False, return_html=True)
    assert '"center": null' not in html
    assert 'forceRadial' in html
    assert '"depth": null' not in html


def test_radialgraph_invalid_center_falls_back_to_highest_degree():
    """An unknown center should warn and fall back to the highest-degree
    node (same as center=None), not collapse everything to radius 0."""
    d3 = D3Blocks(chart='radialgraph', frame=False)
    html = d3.radialgraph(_sample_df(), center='does-not-exist', showfig=False, return_html=True)
    assert '"center": null' not in html
    assert 'forceRadial' in html
