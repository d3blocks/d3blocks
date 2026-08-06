"""RadialGraph block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3

Force-directed network graph, arranged radially by hop-distance from a
focal node - mimicking Obsidian's graph view (both its "local graph" mode,
concentric rings around the current note, and its default "global graph"
force layout). General many-to-many source/target/weight input; no tree/
hierarchy assumption, no single-root flattening.

Node appearance (color/size/opacity/label/tooltip) and edge/link appearance
(color/width/opacity) are delegated to d3graph's own property computation
(cluster coloring, degree-centrality sizing/opacity, weight-scaled edge
width), so a RadialGraph and a D3graph built from the same data and the same
settings resolve to identical values - the two blocks only differ in
layout.

Client-side (in the browser) the user can recompute network statistics
(PageRank, HITS, degree/closeness/betweenness centrality, connected-
component clustering) over the *currently filtered* edge set and use a
single "Network Statistic" selector to drive node color and size together,
matching d3graph's interactive pattern. Optional significance testing is
delegated to d3graph.network_significance() on the Python side.
"""
import json
import numpy as np
import pandas as pd
import networkx as nx
from jinja2 import Environment, PackageLoader

try:
    from .. utils import (
        convert_dataframe_dict, set_path, pre_processing,
        update_config, write_html_file, include_save_to_svg_script,
    )
except Exception:
    from utils import (
        convert_dataframe_dict, set_path, pre_processing,
        update_config, write_html_file, include_save_to_svg_script,
    )

# d3graph is already a d3blocks dependency. Reused for node/edge property
# computation and for network_significance() - not for rendering.
from d3graph import d3graph as _D3Graph, vec2adjmat as _vec2adjmat, data_checks as _data_checks


# Statistics supported by d3graph.network_significance() (degree is
# deliberately unsupported there - degree-preserving randomization has no
# valid null for degree itself).
_SIGNIFICANCE_STATS = (
    'pagerank', 'hits_hub', 'hits_authority', 'closeness', 'betweenness',
)


# %% Set configuration properties
def set_config(config={}, font={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] = 'radialgraph'
    config['title'] = kwargs.get('title', 'RadialGraph - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'radialgraph.html'), logger)
    config['figsize'] = kwargs.get('figsize', [800, 800])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set2')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['font'] = {**{'size': 10}, **font}
    config['notebook'] = kwargs.get('notebook', False)
    config['save_button'] = kwargs.get('save_button', True)

    # Layout / focus
    # center=None -> highest-degree node is chosen as the focus (local rings).
    # center='<node name>' -> concentric rings by BFS hop-distance from that node.
    config['center'] = kwargs.get('center', None)
    config['ring_spacing'] = kwargs.get('ring_spacing', 70)
    config['auto_ring_spacing'] = kwargs.get('auto_ring_spacing', True)
    config['radial_strength'] = kwargs.get('radial_strength', 0.8)
    config['ripple_delay_ms'] = kwargs.get('ripple_delay_ms', 900)

    # Force-simulation knobs - names match d3graph for consistency.
    config['charge'] = kwargs.get('charge', -120)
    config['collision'] = kwargs.get('collision', 1.0)
    config['link_distance'] = kwargs.get('link_distance', 40)
    config['link_strength'] = kwargs.get('link_strength', None)
    config['sticky'] = kwargs.get('sticky', True)
    config['shape'] = kwargs.get('shape', 'circle')

    # Node / edge property defaults - identical to d3graph.graph() defaults.
    config['color'] = kwargs.get('color', 'cluster')
    config['opacity'] = kwargs.get('opacity', 'degree')
    config['size'] = kwargs.get('size', 'degree')
    config['scaler'] = kwargs.get('scaler', 'zscore')
    config['minmax'] = kwargs.get('minmax', [8, 13])
    config['edge_color'] = kwargs.get('edge_color', '#808080')
    # Node *border* defaults (d3graph node_properties['edge_color'/'edge_size']).
    # Kept separate from the link-level edge_color above.
    config['node_edge_color'] = kwargs.get('node_edge_color', '#000000')
    config['node_edge_size'] = kwargs.get('node_edge_size', 1)
    config['edge_opacity'] = kwargs.get('edge_opacity', 'weight')
    config['edge_scaler'] = kwargs.get('edge_scaler', 'zscore')
    config['edge_minmax'] = kwargs.get('edge_minmax', [0.5, 15])
    config['min_weight'] = kwargs.get('min_weight', 1.0)

    # Panel visibility - same default-True convention as d3graph.show_slider /
    # show_controls.
    config['show_stats_panel'] = kwargs.get('show_stats_panel', True)
    config['show_node_panel'] = kwargs.get('show_node_panel', True)
    config['show_controls'] = kwargs.get('show_controls', True)
    config['dark_mode'] = kwargs.get('dark_mode', True)
    config['background_color'] = kwargs.get('background_color', '#12141c')

    # Optional significance testing (Python-side, via d3graph).
    # None = skip (default). One of _SIGNIFICANCE_STATS to run
    # network_significance() and attach node_proba.
    config['significance_test'] = kwargs.get('significance_test', None)
    config['significance_alpha'] = kwargs.get('significance_alpha', 0.05)
    config['significance_n_top'] = kwargs.get('significance_n_top', 100)
    config['significance_n_random'] = kwargs.get('significance_n_random', 1000)
    config['significance_seed'] = kwargs.get('significance_seed', None)

    return config


# %% Set Edge properties
def set_edge_properties(df, **kwargs):
    """Set the edge (link) properties via d3graph.set_edge_properties."""
    logger = kwargs.get('logger', None)
    df = df.copy()
    df = pre_processing(df, labels=df.columns.values[:-1].astype(str))
    # pre_processing reassigns the index to string labels, which breaks
    # alignment inside d3graph's vec2adjmat pivot. Reset before handing off.
    df = df.reset_index(drop=True)

    source_col, target_col, weight_col = df.columns[0], df.columns[1], df.columns[-1]
    # Force plain object dtype so this works on pandas >= 3.0 native str dtype.
    adjmat = _vec2adjmat(
        df[source_col].astype(object),
        df[target_col].astype(object),
        weight=df[weight_col],
    )
    g = _D3Graph(verbose=0)
    g.adjmat = _data_checks(adjmat.copy())
    g.set_edge_properties(
        min_weight=kwargs.get('min_weight', 1.0),
        scaler=kwargs.get('edge_scaler', 'zscore'),
        edge_color=kwargs.get('edge_color', '#808080'),
        edge_opacity=kwargs.get('edge_opacity', 'weight'),
        minmax=kwargs.get('edge_minmax', [0.5, 15]),
    )
    edge_props = g.edge_properties

    def _lookup(row, field, default):
        key = (row[source_col], row[target_col])
        return edge_props.get(key, {}).get(field, default)

    df['edge_color'] = df.apply(lambda r: _lookup(r, 'edge_color', '#999999'), axis=1)
    df['edge_width'] = df.apply(lambda r: _lookup(r, 'weight_scaled', 1), axis=1)
    df['edge_opacity'] = df.apply(lambda r: _lookup(r, 'edge_opacity', 0.6), axis=1)
    df['weight'] = df[weight_col]
    return df


def _resolve_shape(name, shape_cfg):
    """Resolve a node's shape from the 'shape' config."""
    if isinstance(shape_cfg, str):
        return shape_cfg if shape_cfg in ('circle', 'square') else 'circle'
    try:
        value = shape_cfg.get(name) if hasattr(shape_cfg, 'get') else shape_cfg[name]
        return value if value in ('circle', 'square') else 'circle'
    except (KeyError, TypeError, IndexError):
        return 'circle'


def _highest_degree_node(df):
    """Pick the node with the highest undirected degree (ties → first by name)."""
    source_col, target_col = df.columns[0], df.columns[1]
    G = nx.from_pandas_edgelist(df, source=source_col, target=target_col)
    if G.number_of_nodes() == 0:
        return None
    # degree() returns (node, deg); sort by -deg then name for stability.
    ranked = sorted(G.degree(), key=lambda x: (-x[1], str(x[0])))
    return ranked[0][0]


def _compute_depths(df, center, logger=None):
    """BFS hop-distance from `center`. Unreachable nodes get max_depth + 1."""
    if center is None:
        return {}

    source_col, target_col = df.columns[0], df.columns[1]
    G = nx.from_pandas_edgelist(df, source=source_col, target=target_col)

    if center not in G:
        if logger is not None:
            logger.warning(
                f"center='{center}' not found in the graph; falling back "
                "to highest-degree node as focus."
            )
        return {}

    depths = nx.single_source_shortest_path_length(G, center)
    if depths:
        max_depth = max(depths.values())
        for node in G.nodes():
            if node not in depths:
                depths[node] = max_depth + 1
    return depths


def set_node_properties(df, **kwargs):
    """Set the node properties via d3graph.set_node_properties().

    Adds RadialGraph-specific fields: 'depth' (BFS hop from center),
    'shape', and optionally 'proba' (when significance_test is set).

    When center is None, the highest-degree node is chosen as the focus
    so the graph always opens in local-ring mode around a sensible hub.
    """
    logger = kwargs.get('logger', None)
    df = df.reset_index(drop=True)
    source_col, target_col = df.columns[0], df.columns[1]
    weight_col = df.columns[-1] if df.shape[1] > 2 else None
    weight = df[weight_col] if weight_col is not None else None

    adjmat = _vec2adjmat(
        df[source_col].astype(object),
        df[target_col].astype(object),
        weight=weight,
    )
    g = _D3Graph(verbose=0)
    g.adjmat = _data_checks(adjmat.copy())
    g.set_node_properties(
        label=kwargs.get('label'),
        tooltip=kwargs.get('tooltip'),
        color=kwargs.get('color', 'cluster'),
        opacity=kwargs.get('opacity', 'degree'),
        size=kwargs.get('size', 'degree'),
        cmap=kwargs.get('cmap', 'Set2'),
        scaler=kwargs.get('scaler', 'zscore'),
        minmax=kwargs.get('minmax', [8, 13]),
    )
    node_properties = g.node_properties

    # Resolve center: explicit name, else highest-degree node.
    center = kwargs.get('center', None)
    if center is None:
        center = _highest_degree_node(df)
        if logger is not None and center is not None:
            logger.info(f"center=None → using highest-degree node '{center}' as focus.")

    shape_cfg = kwargs.get('shape', 'circle')
    depths = _compute_depths(df, center, logger=logger)

    # If the chosen center wasn't in the graph (e.g. bad name), depths is
    # empty - fall back once more to highest-degree so rings still work.
    if not depths and center is not None:
        center = _highest_degree_node(df)
        depths = _compute_depths(df, center, logger=logger)

    # Node-border defaults. These are the properties the user tweaks via
    #   d3.node_properties['<node>']['edge_color'] = '#FF0000'
    #   d3.node_properties['<node>']['edge_size']  = 10
    # d3graph already emits them for most configurations; fill in anything
    # missing so the keys are always present and settable.
    node_edge_color = kwargs.get('node_edge_color', '#000000')
    node_edge_size = kwargs.get('node_edge_size', 1)

    for name, props in node_properties.items():
        props['depth'] = depths.get(name)
        props['shape'] = _resolve_shape(name, shape_cfg)
        if props.get('edge_color') is None:
            props['edge_color'] = node_edge_color
        if props.get('edge_size') is None:
            props['edge_size'] = node_edge_size
        # Ensure proba key exists (NaN until significance runs).
        if 'proba' not in props:
            props['proba'] = float('nan')

    significance_test = kwargs.get('significance_test', None)
    if significance_test is not None:
        if significance_test not in _SIGNIFICANCE_STATS:
            if logger is not None: logger.warning(f"significance_test='{significance_test}' is not supported (expected one of {_SIGNIFICANCE_STATS}). Skipping.")
        else:
            if logger is not None: logger.info(f"Running network_significance(statistic='{significance_test}')…")
            g.network_significance(
                g.adjmat,
                statistic=significance_test,
                n_top=kwargs.get('significance_n_top', 100),
                n_random=kwargs.get('significance_n_random', 1000),
                alpha=kwargs.get('significance_alpha', 0.05),
                seed=kwargs.get('significance_seed', None),
            )

            # Copy proba values back into our node_properties dict.
            for name, props in node_properties.items():
                if name in g.node_properties and 'proba' in g.node_properties[name]:
                    props['proba'] = g.node_properties[name]['proba']

    return node_properties


def _build_graph_json(df, node_properties, logger=None):
    """Build the flat {nodes, links} JSON the client consumes."""
    source_col, target_col = df.columns[0], df.columns[1]
    node_names = pd.unique(df[[source_col, target_col]].values.ravel())

    # The center is, by construction, whichever node set_node_properties()
    # gave depth 0 - deriving it this way (instead of smuggling it through
    # node_properties as an extra key) means node_properties only ever
    # contains real per-node dicts, so callers can safely iterate
    # .values()/.items() without special-casing a stash entry.
    center = None
    if isinstance(node_properties, dict):
        for name, props in node_properties.items():
            if isinstance(props, dict) and props.get('depth') == 0:
                center = name
                break

    # Helper to tolerate slight label normalization differences (spaces → underscores, trimmed, or quoted)
    def _get_props(name, node_props):
        if not node_props:
            return {}
        # Fast path: exact match
        if name in node_props:
            return node_props[name]
        s = str(name)
        # Try trimmed
        if s.strip() in node_props:
            return node_props[s.strip()]
        # Try underscore variant
        us = s.strip().replace(' ', '_')
        if us in node_props:
            return node_props[us]
        # Try removing quotes
        rq = s.replace("'", "")
        if rq in node_props:
            return node_props[rq]
        # Last resort: stringified-key equality
        for k, v in node_props.items():
            try:
                if str(k) == s:
                    return v
            except Exception:
                continue
        return {}

    def _as_float(value, default=None):
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    nodes = []
    for name in node_names:
        props = _get_props(name, node_properties or {})
        proba = props.get('proba', float('nan'))
        try:
            proba_val = float(proba)
        except (TypeError, ValueError):
            proba_val = float('nan')
        nodes.append({
            'id': str(name),
            'color': props.get('color', '#D33F6A'),
            'baseColor': props.get('color', '#D33F6A'),
            'size': float(props.get('size', 10) or 10),
            'baseSize': float(props.get('size', 10) or 10),
            'opacity': float(props.get('opacity', 0.95) if props.get('opacity') is not None else 0.95),
            'tooltip': props.get('tooltip', str(name)),
            'label': props.get('label', str(name)),
            'shape': props.get('shape', 'circle'),
            'depth': props.get('depth', None),
            'fontcolor': props.get('fontcolor', props.get('color', '#dcddde')),
            'fontsize': float(props.get('fontsize', 10) or 10),
            # Node BORDER styling (d3graph semantics): stroke color + width
            # of the node circle/square itself, not of its links.
            'edge_color': props.get('edge_color', None),
            'edge_size': _as_float(props.get('edge_size')),
            # node_proba mirrors d3graph's JSON field name so the shared
            # statMetric selector vocabulary transfers cleanly.
            'node_proba': proba_val,
        })

    links = []
    for _, row in df.iterrows():
        src = str(row[source_col])
        tgt = str(row[target_col])
        # Link styling comes from the per-edge columns only. The per-node
        # 'edge_color'/'edge_size' properties describe the node border and
        # must not bleed into link appearance.
        link_color = row.get('edge_color') if row.get('edge_color') is not None else '#999999'
        link_width = _as_float(row.get('edge_width'), 1.0) or 1.0
        link_opacity = _as_float(row.get('edge_opacity'), 0.6)
        if link_opacity is None:
            link_opacity = 0.6

        links.append({
            'source': src,
            'target': tgt,
            'weight': float(row.get('weight', 1) or 1),
            'link_color': link_color,
            'link_width': link_width,
            'link_opacity': link_opacity,
        })

    payload = {'nodes': nodes, 'links': links, 'rootId': str(center) if center is not None else None}
    return json.dumps(payload, indent=2, default=str), center


def show(df, **kwargs):
    """Build and show the graph."""
    df = df.copy()
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    node_properties = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df.copy(), frame=True)
    df.reset_index(inplace=True, drop=True)

    X, resolved_center = _build_graph_json(df, node_properties, logger=logger)
    # Keep config.center in sync with whatever was actually resolved
    # (highest-degree fallback, or the caller's explicit choice).
    if resolved_center is not None:
        config['center'] = resolved_center

    X = str(X).replace("'", '"')
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html."""
    save_script, show_save_button = include_save_to_svg_script(
        config.get('save_button', True), title=config.get('title', 'RadialGraph')
    )
    width = 'window.innerWidth' if config['figsize'][0] is None else config['figsize'][0]
    height = 'null' if config['figsize'][1] is None else config['figsize'][1]

    content = {
        'json_data': X,
        'TITLE': config.get('title', 'RadialGraph - D3blocks'),
        'WIDTH': width,
        'HEIGHT': height,
        'fontsize': config.get('font', {}).get('size', 10),
        'center': json.dumps(config.get('center')),
        'ringSpacing': config.get('ring_spacing', 70),
        'autoRingSpacing': 'true' if config.get('auto_ring_spacing', True) else 'false',
        'radialStrength': config.get('radial_strength', 0.8),
        'rippleDelayMs': config.get('ripple_delay_ms', 900),
        'charge': config.get('charge', -120),
        'collision': config.get('collision', 1.0),
        'linkDistance': config.get('link_distance', 40),
        'linkStrength': 'null' if config.get('link_strength') is None else config.get('link_strength'),
        'sticky': 'true' if config.get('sticky', True) else 'false',
        'showStatsPanel': 'true' if config.get('show_stats_panel', True) else 'false',
        'showNodePanel': 'true' if config.get('show_node_panel', True) else 'false',
        'showControls': 'true' if config.get('show_controls', True) else 'false',
        'darkMode': 'true' if config.get('dark_mode', True) else 'false',
        'backgroundColor': config.get('background_color', '#12141c'),
        'SIGNIFICANCE_ALPHA': config.get('significance_alpha', 0.05),
        'SUPPORT': config.get('support', ''),
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except Exception:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.radialgraph', package_path='d3js'))

    index_template = jinja_env.get_template('radialgraph.html.j2')
    html = index_template.render(content)
    write_html_file(config, html, logger)
    return html