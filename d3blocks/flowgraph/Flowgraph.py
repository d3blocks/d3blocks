"""Flowgraph block.

Layered diagrams for process flows and architecture diagrams. Nodes are placed
in ranks with dagre or ELK (Sugiyama-style layered layouts), drawn as flowchart
shapes and can be nested in groups (swimlanes, system boundaries, VPCs, ...).
Input is an edge list or a Mermaid flowchart.

Library     : d3blocks
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import json
import os
import re
from html import escape as html_escape
from pathlib import Path

import colourmap
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader, PackageLoader

try:
    from ..utils import set_path, update_config, write_html_file, set_logo, resolve_color_background
except ImportError:
    from utils import set_path, update_config, write_html_file, set_logo, resolve_color_background


SHAPES = ('process', 'decision', 'terminal', 'io', 'subprocess', 'database',
          'queue', 'document', 'external', 'circle')
DIRECTIONS = ('LR', 'TB', 'RL', 'BT')
CURVES = ('smooth', 'straight')
EDGE_STYLES = ('solid', 'dashed', 'dotted')
RANKERS = ('network-simplex', 'tight-tree', 'longest-path')
LAYOUTS = ('dagre', 'elk')
ANIMATIONS = ('none', 'pulse', 'dash', 'dots', 'comet')
# Semantic edge variants (after archify): colour, line style and extra width.
# An edge's own 'color' / 'style' columns override these.
EDGE_VARIANTS = {
    'default': {'color': None, 'style': 'solid', 'width': 0},
    'emphasis': {'color': '#f28e2b', 'style': 'solid', 'width': 1.5},
    'security': {'color': '#b07aa1', 'style': 'solid', 'width': 0.5},
    'async': {'color': '#4e79a7', 'style': 'dashed', 'width': 0},
    'error': {'color': '#e15759', 'style': 'dotted', 'width': 0.5},
}
DEFAULT_NODE_COLOR = '#1ABC9C'
DEFAULT_EDGE_COLOR = '#8c8c8c'


# %% Set configuration properties
def set_config(config={}, font={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] = 'flowgraph'
    config['title'] = kwargs.get('title', 'Flowgraph - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'flowgraph.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['font'] = {**{'size': 13}, **font}
    # Layout
    # 'TD' is accepted as in Mermaid (same as 'TB').
    direction = str(kwargs.get('direction', 'LR')).upper()
    config['direction'] = _check_choice(_MERMAID_DIRECTIONS.get(direction, direction), DIRECTIONS, 'direction', 'LR', logger, upper=True)
    config['nodesep'] = kwargs.get('nodesep', 40)
    config['ranksep'] = kwargs.get('ranksep', 70)
    config['edgesep'] = kwargs.get('edgesep', 20)
    config['ranker'] = _check_choice(kwargs.get('ranker', 'network-simplex'), RANKERS, 'ranker', 'network-simplex', logger)
    config['layout'] = _check_choice(kwargs.get('layout', 'dagre'), LAYOUTS, 'layout', 'dagre', logger)
    config['draggable'] = kwargs.get('draggable', True)
    # Edges
    config['curve'] = _check_choice(kwargs.get('curve', 'smooth'), CURVES, 'curve', 'smooth', logger)
    config['animate'], config['animation'] = _resolve_animate(kwargs.get('animate', False), logger)
    config['show_edge_labels'] = kwargs.get('show_edge_labels', True)
    # Groups: {group: {'label': str, 'parent': str or None, 'color': hex}}
    config['groups'] = kwargs.get('groups') or {}
    config['cmap'] = kwargs.get('cmap', 'Set2')
    config['show_groups'] = kwargs.get('show_groups', True)
    # GUI
    config['color_background'] = kwargs.get('color_background', None)
    config['dark_mode'] = kwargs.get('dark_mode', True)
    config['save_button'] = kwargs.get('save_button', True)
    config['show_side_panel'] = kwargs.get('show_side_panel', True)
    config['show_top_panel'] = kwargs.get('show_top_panel', True)
    return config


# %% Node properties
def set_node_properties(df, nodes=None, shape='process', color='group', cmap='Set2', logger=None, **kwargs):
    """Set the node properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Edges with at least the columns 'source' and 'target'.
    nodes : pd.DataFrame or dict, (default: None)
        Optional per-node attributes, keyed by node name. Accepted columns/keys:
        'label', 'shape', 'group', 'color', 'tooltip'. A DataFrame may hold the
        node name in a 'name' column or in its index. Nodes listed here that do
        not occur in `df` are drawn as isolated nodes.
    shape : str, (default: 'process')
        Default shape for nodes without one. One of: SHAPES.
    color : str, (default: 'group')
        * 'group': colour by group (nodes without a group get the default colour).
        * 'shape': colour by shape.
        * '#RRGGBB': one colour for every node.
        A per-node 'color' in `nodes` always wins.
    cmap : str, (default: 'Set2')
        Matplotlib colormap used for 'group' / 'shape' colouring.

    Returns
    -------
    dict
        {node_name: {'name', 'label', 'shape', 'group', 'color', 'tooltip'}}

    """
    _check_columns(df)
    shape = _check_choice(shape, SHAPES, 'shape', 'process', logger)
    attrs = _nodes_to_dict(nodes)

    # Node order: first appearance in the edge list, then isolated nodes.
    order = list(pd.unique(df[['source', 'target']].astype(str).values.ravel()))
    order += [n for n in attrs if n not in order]

    unknown = [n for n in attrs if n not in set(df['source'].astype(str)) | set(df['target'].astype(str))]
    if unknown and logger is not None:
        logger.info('Nodes without edges are drawn isolated: %s' % unknown)

    node_properties = {}
    for name in order:
        a = attrs.get(name, {})
        node_shape = _check_choice(_get(a, 'shape', shape), SHAPES, f"shape of '{name}'", shape, logger)
        label = str(_get(a, 'label', name))
        group = _get(a, 'group', None)
        node_properties[name] = {
            'name': name,
            'label': label,
            'shape': node_shape,
            'group': None if group is None else str(group),
            'color': _get(a, 'color', None),
            'tooltip': _optional_str(_get(a, 'tooltip', None)),
        }

    _assign_colors(node_properties, color, cmap)
    return node_properties


# %% Group properties
def set_group_properties(node_properties, groups=None, cmap='Set2', logger=None):
    """Collect the groups used by the nodes and fill in label/parent/colour.

    Parameters
    ----------
    node_properties : dict or pd.DataFrame
        Output of set_node_properties().
    groups : dict, (default: None)
        Optional {group: {'label': str, 'parent': str, 'color': hex}} or the short
        form {group: parent}. Use 'parent' to nest groups, e.g. a subnet inside a VPC.

    Returns
    -------
    dict
        {group: {'name', 'label', 'parent', 'color'}}

    """
    node_properties = _node_properties_to_dict(node_properties)
    groups = dict(groups or {})
    groups = {str(k): (v if isinstance(v, dict) else {'parent': v}) for k, v in groups.items()}

    names = [p['group'] for p in node_properties.values() if p['group'] is not None]
    names += list(groups)
    # Parents must exist as groups too.
    for g in list(names):
        parent = groups.get(g, {}).get('parent')
        while parent is not None and parent not in names:
            names.append(parent)
            parent = groups.get(parent, {}).get('parent')
    names = list(dict.fromkeys(str(g) for g in names))

    # Colour groups the same way nodes are coloured by group, so they match.
    node_group_color = {}
    for p in node_properties.values():
        if p['group'] is not None:
            node_group_color.setdefault(p['group'], p['color'])
    fallback = _colors_for(names, cmap)

    group_properties = {}
    for g in names:
        cfg = groups.get(g, {})
        parent = cfg.get('parent')
        if parent is not None and str(parent) == g:
            if logger is not None: logger.warning("Group '%s' cannot be its own parent; ignoring." % g)
            parent = None
        group_properties[g] = {
            'name': g,
            'label': str(cfg.get('label', g)),
            'parent': None if parent is None else str(parent),
            'color': cfg.get('color') or node_group_color.get(g) or fallback[g],
        }

    if _has_parent_cycle(group_properties):
        raise ValueError('Group parents form a cycle; check the "parent" entries in `groups`.')
    return group_properties


# %% Edge properties
def set_edge_properties(df, edge_color='#8c8c8c', logger=None, **kwargs):
    """Set the edge properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Required columns: 'source', 'target'.
        Optional columns:
            * 'label': text on the edge.
            * 'weight': line width (scaled when weights differ).
            * 'variant': 'default', 'emphasis', 'security', 'async' or 'error';
              sets colour, line style and width (see EDGE_VARIANTS).
            * 'style': 'solid', 'dashed' or 'dotted'; overrides the variant.
            * 'color': edge colour; overrides the variant and `edge_color`.
            * 'animation': 'none', 'pulse', 'dash', 'dots' or 'comet'; overrides
              the chart-wide animation for this edge.
    edge_color : str, (default: '#8c8c8c')
        Colour of 'default' edges without their own 'color':
            * '#RRGGBB': one colour.
            * 'source': colour of the source node.
            * 'target': colour of the target node.
    node_properties : dict or pd.DataFrame, (optional, via kwargs)
        Needed for edge_color='source' / 'target'.

    Returns
    -------
    pd.DataFrame
        One row per edge with the columns source, target, label, weight, variant,
        style, color, width, animation.

    """
    _check_columns(df)
    out = pd.DataFrame({
        'source': df['source'].astype(str).values,
        'target': df['target'].astype(str).values,
    })
    out['label'] = _column(df, 'label', '').fillna('').astype(str).values
    out['weight'] = pd.to_numeric(_column(df, 'weight', 1), errors='coerce').fillna(1).astype(float).values

    variants = _column(df, 'variant', 'default').fillna('default').astype(str).str.lower()
    _warn_unknown(variants, EDGE_VARIANTS, 'edge variant', 'default', logger)
    out['variant'] = variants.where(variants.isin(list(EDGE_VARIANTS)), 'default').values

    preset_style = out['variant'].map(lambda v: EDGE_VARIANTS[v]['style'])
    styles = _column(df, 'style', None).astype(object).str.lower()
    _warn_unknown(styles.dropna(), EDGE_STYLES, 'edge style', 'solid', logger)
    styles = styles.where(styles.isin(EDGE_STYLES), None)
    out['style'] = styles.where(styles.notna(), preset_style.values).values

    # Colour: explicit 'color' > variant colour > edge_color (hex, 'source', 'target').
    node_colors = {}
    if edge_color in ('source', 'target'):
        node_colors = {k: v.get('color') for k, v in _node_properties_to_dict(kwargs.get('node_properties')).items()}
    end = out['source'] if edge_color == 'source' else out['target']
    base = end.map(node_colors).fillna(DEFAULT_EDGE_COLOR) if edge_color in ('source', 'target') else pd.Series(edge_color, index=out.index)
    preset_color = out['variant'].map(lambda v: EDGE_VARIANTS[v]['color'])
    colors = _column(df, 'color', None).astype(object)
    colors = colors.where(colors.notna(), preset_color.values)
    out['color'] = colors.where(colors.notna(), base.values).astype(str).values

    anims = _column(df, 'animation', None).astype(object).str.lower()
    _warn_unknown(anims.dropna(), ANIMATIONS, 'edge animation', 'chart default', logger)
    out['animation'] = anims.where(anims.isin(ANIMATIONS), None).values

    # Line width follows weight when weights differ, otherwise a constant width.
    w = out['weight'].values
    if len(w) and np.ptp(w) > 0:
        width = 1.5 + 3.5 * (w - w.min()) / np.ptp(w)
    else:
        width = np.full(len(w), 1.5)
    out['width'] = np.round(width + out['variant'].map(lambda v: EDGE_VARIANTS[v]['width']).values, 2)

    selfloops = out['source'] == out['target']
    if selfloops.any() and logger is not None:
        logger.info('Self-loops are drawn but may overlap the node: %s' % out.loc[selfloops, 'source'].tolist())
    return out


# %% Show
def show(df, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Edge properties (output of set_edge_properties).
    config : dict
        Configuration keys.
    node_properties : dict or pd.DataFrame
        Node properties (output of set_node_properties).

    Returns
    -------
    str
        The generated HTML.

    """
    logger = kwargs.get('logger', None)
    node_properties = _node_properties_to_dict(kwargs.get('node_properties'))
    config = update_config(kwargs, logger).copy()

    # Edges may reference nodes that were added after set_node_properties().
    for name in pd.unique(df[['source', 'target']].values.ravel()):
        if name not in node_properties:
            node_properties[name] = {'name': name, 'label': name, 'shape': 'process', 'group': None,
                                     'color': DEFAULT_NODE_COLOR, 'tooltip': None}

    # Groups are resolved here only, from the user's settings in config['groups'], so
    # colours follow the current node colours and the chart's cmap on every redraw.
    groups = set_group_properties(node_properties, config.get('groups'), cmap=config.get('cmap', 'Set2'), logger=logger)

    # Per-edge animations play even when the chart-wide animation is off.
    if 'animation' in df.columns and df['animation'].notna().any() and not config.get('animate'):
        config['animate'], config['animation'] = True, 'none'

    data = {
        'nodes': [_jsonable(p) for p in node_properties.values()],
        'edges': [_jsonable(r) for r in df.to_dict(orient='records')],
        'groups': [_jsonable(g) for g in groups.values()],
    }
    X = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')

    config['logo_base64'] = set_logo(filepath=config.get('logo'))
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : str
        JSON string with nodes, edges and groups.
    config : dict
        Configuration keys.

    Returns
    -------
    str
        The generated HTML.

    """
    bg_dark, bg_light = resolve_color_background(config.get('color_background', None))
    save_button = config.get('save_button', True)
    options = {
        'direction': config['direction'],
        'nodesep': config['nodesep'],
        'ranksep': config['ranksep'],
        'edgesep': config['edgesep'],
        'ranker': config['ranker'],
        'layout': config.get('layout', 'dagre'),
        'draggable': bool(config.get('draggable', True)),
        'curve': config['curve'],
        'animate': bool(config['animate']),
        'animation': config.get('animation', 'pulse'),
        'showEdgeLabels': bool(config['show_edge_labels']),
        'showGroups': bool(config['show_groups']),
        'fontsize': config['font']['size'],
        'width': config['figsize'][0],
        'height': config['figsize'][1],
        'title': config['title'],
    }

    content = {
        'json_data': X,
        'options': json.dumps(options).replace('</', '<\\/'),
        'TITLE': html_escape(str(config['title'])),
        'COLOR_BACKGROUND_DARK': bg_dark,
        'COLOR_BACKGROUND_LIGHT': bg_light,
        'fontsize': config['font']['size'],
        'nodesep': config['nodesep'],
        'ranksep': config['ranksep'],
        'layout': config.get('layout', 'dagre'),
        'darkMode': 'true' if config.get('dark_mode', True) else 'false',
        'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
        'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
        'SUPPORT': config.get('support') or '',
        'SAVE_BUTTON_START': '' if save_button else '<!--',
        'SAVE_BUTTON_STOP': '' if save_button else '-->',
        'LOGO_BASE64': config['logo_base64'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except Exception:
        from pathlib import Path
        jinja_env = Environment(loader=FileSystemLoader(str(Path(__file__).resolve().parent / 'd3js')))

    html = jinja_env.get_template('flowgraph.html.j2').render(content)
    write_html_file(config, html, logger)
    return html


# %% Mermaid
_MERMAID_SHAPES = [
    # (open, close, shape), longest delimiters first.
    ('(((', ')))', 'circle'),
    ('([', '])', 'terminal'),
    ('[[', ']]', 'subprocess'),
    ('[(', ')]', 'database'),
    ('((', '))', 'circle'),
    ('{{', '}}', 'process'),
    ('[/', '/]', 'io'),
    ('[\\', '\\]', 'io'),
    ('[/', '\\]', 'io'),
    ('[\\', '/]', 'io'),
    ('[', ']', 'process'),
    ('(', ')', 'process'),
    ('{', '}', 'decision'),
    ('>', ']', 'document'),
]
_MERMAID_DIRECTIONS = {'LR': 'LR', 'RL': 'RL', 'TB': 'TB', 'TD': 'TB', 'BT': 'BT'}
_MERMAID_ID = re.compile(r'[A-Za-z0-9_]+')
# Link with inline text: -- text -->, -. text .->, == text ==>
_MERMAID_LINK_TEXT = re.compile(r'(--|==|-\.)\s+(.+?)\s+(-{2,}>|-{3,}|={2,}>|={3,}|\.-+>|\.-+)')
# Plain link: -->, ---, -.->, ==>, ~~~, <-->, --o, --x
_MERMAID_LINK = re.compile(r'<?(-{2,}|={2,}|-\.+-|~{3,})(>|o(?=\s)|x(?=\s))?')
_MERMAID_SKIP = {'linkStyle', 'click', 'accTitle', 'accDescr', 'direction'}


MERMAID_FILE_SUFFIXES = ('.md', '.markdown', '.mmd', '.mermaid')


def is_mermaid_source(obj):
    """True for str / path-like input, which is read as Mermaid (see read_mermaid)."""
    return isinstance(obj, (str, os.PathLike))


def read_mermaid(source, logger=None):
    """Return Mermaid flowchart text from text, Markdown or a file path.

    Parameters
    ----------
    source : str or path-like
        * Mermaid flowchart text.
        * Markdown text with ```mermaid fenced blocks.
        * Path to a .md / .markdown file (fenced blocks) or a .mmd / .mermaid file.
        From Markdown, the first fenced block that is a flowchart ('flowchart' or
        'graph') is used; other diagram types are skipped.

    Returns
    -------
    str
        Mermaid flowchart text.

    """
    path = _as_mermaid_path(source)
    text = path.read_text(encoding='utf-8') if path is not None else str(source)
    blocks = re.findall(r'^[ \t]*```+[ \t]*mermaid[^\n]*\n(.*?)^[ \t]*```', text, re.S | re.M)
    if not blocks:
        return text
    flowcharts = [b for b in blocks if _first_statement(b).split()[:1] in (['flowchart'], ['graph'], ['flowchart-elk'])]
    if not flowcharts:
        raise ValueError('No Mermaid flowchart found in the ```mermaid blocks of %s.' % (path or 'the Markdown text'))
    if len(flowcharts) > 1 and logger is not None:
        logger.info('Found %d Mermaid flowcharts; using the first.' % len(flowcharts))
    return flowcharts[0]


def _as_mermaid_path(source):
    """Path to read, or None when `source` is diagram text.

    Paths with other suffixes (e.g. a CSV) raise a ValueError instead of being
    parsed as diagram text.
    """
    if isinstance(source, os.PathLike):
        path = Path(source)
    elif isinstance(source, str) and '\n' not in source and _looks_like_path(source.strip()):
        path = Path(source.strip())
    else:
        return None
    if path.suffix.lower() not in MERMAID_FILE_SUFFIXES:
        raise ValueError('Unsupported input file %s: use a Mermaid/Markdown file (%s), or load the data into a '
                         'DataFrame with source/target columns.' % (path, ', '.join(MERMAID_FILE_SUFFIXES)))
    if not path.is_file():
        raise FileNotFoundError('Mermaid/Markdown file not found: %s' % path)
    return path


def _looks_like_path(text):
    """A single token ending in a file suffix, e.g. 'docs/flow.md' or 'edges.csv'."""
    return bool(re.fullmatch(r'[^\s;|<>{}\[\]()"]+\.[A-Za-z0-9]{1,10}', text))


def _first_statement(text):
    for line in str(text).splitlines():
        line = line.strip()
        if line and not line.startswith('%%'):
            return line
    return ''


def from_mermaid(text, logger=None):
    """Convert a Mermaid flowchart into Flowgraph inputs.

    Supported: the 'flowchart'/'graph' header with direction, node shapes
    ([] () ([]) [[]] [()] (()) {} {{}} [//] [\\] >]), quoted labels and <br>,
    links (--> --- -.-> ==> ~~~ with |text| or inline text), chains (A --> B --> C),
    '&' (A & B --> C), nested subgraphs, and node colours from 'style' and
    'classDef' + 'class' / ':::'. Other statements are ignored.

    Parameters
    ----------
    text : str or path-like
        Mermaid flowchart text, Markdown with a ```mermaid block, or a path to a
        .md / .markdown / .mmd / .mermaid file (see read_mermaid).

    Returns
    -------
    tuple
        (edges DataFrame, nodes dict, groups dict, direction or None)

    """
    text = read_mermaid(text, logger=logger)
    nodes, groups, edges, classes = {}, {}, [], {}
    stack, direction = [], None

    def node(name, label=None, shape=None):
        n = nodes.setdefault(name, {})
        if label is not None:
            n['label'] = label
        if shape is not None:
            n['shape'] = shape
        if stack and 'group' not in n:
            n['group'] = stack[-1]
        return n

    for raw in _mermaid_statements(text):
        stmt = raw.strip()
        if not stmt or stmt.startswith('%%'):
            continue
        head = stmt.split()[0]
        if head in ('flowchart', 'graph', 'flowchart-elk'):
            parts = stmt.split()
            if len(parts) > 1:
                direction = _MERMAID_DIRECTIONS.get(parts[1].upper(), direction)
            continue
        if head == 'subgraph':
            gid, label = _mermaid_subgraph(stmt[len('subgraph'):].strip())
            groups[gid] = {'label': label, 'parent': stack[-1] if stack else None}
            stack.append(gid)
            continue
        if stmt == 'end':
            if stack:
                stack.pop()
            continue
        if head == 'style':
            parts = stmt.split(None, 2)
            color = _mermaid_color(parts[2] if len(parts) > 2 else '')
            if color:
                node(parts[1])['color'] = color
            continue
        if head == 'classDef':
            parts = stmt.split(None, 2)
            if len(parts) > 2:
                for name in parts[1].split(','):
                    classes[name] = _mermaid_color(parts[2])
            continue
        if head == 'class':
            parts = stmt.split()
            if len(parts) >= 3:
                for name in parts[1].split(','):
                    node(name)['class'] = parts[2]
            continue
        if head.split(':')[0] in _MERMAID_SKIP:
            continue
        # All or nothing: nodes and edges of a statement are kept only if it parses.
        pending, chain_edges = [], []

        def record(name, label=None, shape=None):
            extra = {}
            pending.append((name, label, shape, extra))
            return extra
        try:
            _mermaid_chain(stmt, record, chain_edges)
        except ValueError as e:
            if logger is not None:
                logger.warning('Mermaid: skipped statement %r (%s)' % (stmt, e))
            continue
        for name, label, shape, extra in pending:
            node(name, label, shape).update(extra)
        edges.extend(chain_edges)

    for n in nodes.values():
        cls = n.pop('class', None)
        if cls and classes.get(cls) and 'color' not in n:
            n['color'] = classes[cls]

    linked_groups = sorted(set(groups) & {n for e in edges for n in e[:2]})
    if linked_groups and logger is not None:
        logger.warning('Mermaid: links to subgraphs are not supported; %s are drawn as plain nodes.' % linked_groups)

    if not nodes:
        raise ValueError('No Mermaid flowchart nodes found. Expected text such as '
                         '"flowchart LR; A[Start] --> B{Valid?}", Markdown with a ```mermaid block, '
                         'or a path to a %s file.' % '/'.join(MERMAID_FILE_SUFFIXES))
    df = pd.DataFrame(edges, columns=['source', 'target', 'label', 'style', 'weight'])
    return df, nodes, groups, direction


def merge_group_attributes(base, override):
    """Merge group settings per field; values in `override` win.

    Both accept {group: {'label', 'parent', 'color'}} or the short form {group: parent}.
    """
    def norm(groups):
        return {str(k): (dict(v) if isinstance(v, dict) else {'parent': v}) for k, v in (groups or {}).items()}
    merged = norm(base)
    for name, attrs in norm(override).items():
        merged.setdefault(name, {}).update({k: v for k, v in attrs.items() if not _is_missing(v)})
    return merged


def merge_node_attributes(base, override):
    """Merge per-node attribute dicts; values in `override` win."""
    merged = {k: dict(v) for k, v in (base or {}).items()}
    for name, attrs in _nodes_to_dict(override).items():
        merged.setdefault(name, {}).update({k: v for k, v in attrs.items() if not _is_missing(v)})
    return merged


def _mermaid_statements(text):
    """Split on newlines and on ';' outside quotes, brackets and |edge labels|."""
    out = []
    for line in str(text).splitlines():
        buf, depth, quoted, piped = '', 0, False, False
        for ch in line:
            if ch == '"' and not piped:
                quoted = not quoted
            elif ch == '|' and not quoted and depth == 0:
                piped = not piped
            elif not quoted and not piped and ch in '[({':
                depth += 1
            elif not quoted and not piped and ch in '])}':
                depth = max(0, depth - 1)
            if ch == ';' and not quoted and not piped and depth == 0:
                out.append(buf)
                buf = ''
            else:
                buf += ch
        out.append(buf)
    return out


def _mermaid_label(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    return text.replace('#quot;', '"').strip()


def _mermaid_subgraph(rest):
    m = re.match(r'([A-Za-z0-9_]+)\s*\[(.*)\]\s*$', rest)
    if m:
        return m.group(1), _mermaid_label(m.group(2))
    label = _mermaid_label(rest) or 'group'
    return (rest if _MERMAID_ID.fullmatch(rest) else label), label


def _mermaid_color(spec):
    props = dict(p.split(':', 1) for p in spec.replace(';', ',').split(',') if ':' in p)
    props = {k.strip(): v.strip() for k, v in props.items()}
    return props.get('fill') or props.get('stroke')


def _mermaid_node(stmt, i, node):
    """Parse one node reference at stmt[i]; return (name, new index)."""
    m = _MERMAID_ID.match(stmt, i)
    if not m:
        raise ValueError('expected a node id at %r' % stmt[i:i + 20])
    name, i = m.group(0), m.end()
    label = shape = None
    # Longest opening delimiter first. Of the closings that pair with it, the
    # nearest one ends the label, so '[/a\] --> B[/b/]' stays two nodes.
    for open_ in dict.fromkeys(o for o, _, _ in _MERMAID_SHAPES):
        if not stmt.startswith(open_, i):
            continue
        j = i + len(open_)
        best = None
        for o, close, kind in _MERMAID_SHAPES:
            if o != open_:
                continue
            if stmt.startswith('"', j):
                q = stmt.find('"', j + 1)
                end = q + 1 if q >= 0 and stmt.startswith(close, q + 1) else -1
            else:
                end = stmt.find(close, j)
            if end >= 0 and (best is None or end < best[0]):
                best = (end, close, kind)
        if best is None:
            continue
        end, close, shape = best
        label, i = _mermaid_label(stmt[j:end]), end + len(close)
        break
    node(name, label, shape)
    if stmt.startswith(':::', i):
        m = _MERMAID_ID.match(stmt, i + 3)
        if m:
            node(name)['class'] = m.group(0)
            i = m.end()
    return name, i


def _mermaid_group(stmt, i, node):
    """Parse 'A & B & C'; return (names, new index)."""
    names = []
    while True:
        while i < len(stmt) and stmt[i].isspace():
            i += 1
        name, i = _mermaid_node(stmt, i, node)
        names.append(name)
        j = i
        while j < len(stmt) and stmt[j].isspace():
            j += 1
        if j < len(stmt) and stmt[j] == '&':
            i = j + 1
            continue
        return names, i


def _mermaid_chain(stmt, node, edges):
    """Parse 'A --> B -->|x| C & D' and append edges."""
    left, i = _mermaid_group(stmt, 0, node)
    while True:
        while i < len(stmt) and stmt[i].isspace():
            i += 1
        if i >= len(stmt):
            return
        m = _MERMAID_LINK_TEXT.match(stmt, i)
        if m:
            arrow, label, i = m.group(1) + m.group(3), m.group(2), m.end()
        else:
            m = _MERMAID_LINK.match(stmt, i)
            if not m:
                raise ValueError('expected a link at %r' % stmt[i:i + 20])
            arrow, label, i = m.group(0), '', m.end()
            p = re.compile(r'\s*\|([^|]*)\|').match(stmt, i)
            if p:
                label, i = p.group(1), p.end()
        right, i = _mermaid_group(stmt, i, node)
        if '~' not in arrow:
            style = 'dotted' if '.' in arrow else 'solid'
            weight = 3 if '=' in arrow else 1
            for s in left:
                for t in right:
                    edges.append((s, t, _mermaid_label(label), style, weight))
        left = right


# %% Helpers
def _resolve_animate(animate, logger=None):
    """animate: bool or one of ANIMATIONS -> (enabled, default animation)."""
    if isinstance(animate, (bool, np.bool_)) or animate is None:
        return bool(animate), 'pulse'
    style = _check_choice(animate, ANIMATIONS, 'animate', 'pulse', logger)
    return style != 'none', ('pulse' if style == 'none' else style)


def _warn_unknown(values, allowed, what, fallback, logger):
    bad = sorted(set(values) - set(allowed))
    if bad and logger is not None:
        logger.warning('Unknown %s(s) %s; using %s. Choose from %s.' % (what, bad, fallback, tuple(allowed)))


def _optional_str(v):
    return None if v is None else str(v)


def _check_columns(df):
    missing = [c for c in ('source', 'target') if c not in df.columns]
    if missing:
        raise ValueError('Input DataFrame is missing column(s) %s; found %s.' % (missing, list(df.columns)))


def _check_choice(value, choices, name, default, logger=None, upper=False):
    v = str(value).upper() if upper else str(value).lower()
    if v in choices:
        return v
    if logger is not None:
        logger.warning("Unknown %s '%s'; using '%s'. Choose from %s." % (name, value, default, choices))
    return default


def _is_missing(v):
    return v is None or (isinstance(v, float) and np.isnan(v))


def _get(d, key, default):
    v = d.get(key, default)
    return default if _is_missing(v) else v


def _column(df, name, default):
    return df[name] if name in df.columns else pd.Series([default] * len(df), index=df.index)


def _nodes_to_dict(nodes):
    if nodes is None:
        return {}
    if isinstance(nodes, dict):
        return {str(k): dict(v) for k, v in nodes.items()}
    if isinstance(nodes, pd.DataFrame):
        frame = nodes.set_index('name') if 'name' in nodes.columns else nodes
        return {str(k): {c: v for c, v in row.items()} for k, row in frame.to_dict(orient='index').items()}
    raise TypeError('`nodes` must be a pandas DataFrame or a dict keyed by node name.')


def _node_properties_to_dict(node_properties):
    if isinstance(node_properties, pd.DataFrame):
        frame = node_properties.set_index('name', drop=False) if 'name' in node_properties.columns else node_properties
        node_properties = frame.to_dict(orient='index')
    out = {}
    for name, p in (node_properties or {}).items():
        p = {k: (None if _is_missing(v) else v) for k, v in dict(p).items()}
        p.setdefault('name', str(name))
        out[str(name)] = p
    return out


def _colors_for(keys, cmap):
    keys = list(keys)
    if not keys:
        return {}
    c_hex, _ = colourmap.fromlist(keys, cmap=cmap, scheme='hex', method='matplotlib', verbose=0)
    return dict(zip(keys, c_hex))


def _assign_colors(node_properties, color, cmap):
    if color in ('group', 'shape'):
        keys = sorted({str(p[color]) for p in node_properties.values() if p[color] is not None})
        palette = _colors_for(keys, cmap)
        for p in node_properties.values():
            if p['color'] is None:
                key = p[color]
                p['color'] = palette.get(str(key), DEFAULT_NODE_COLOR) if key is not None else DEFAULT_NODE_COLOR
    else:
        for p in node_properties.values():
            if p['color'] is None:
                p['color'] = color or DEFAULT_NODE_COLOR


def _has_parent_cycle(groups):
    for g in groups:
        seen, cur = set(), g
        while cur is not None:
            if cur in seen:
                return True
            seen.add(cur)
            cur = groups.get(cur, {}).get('parent')
    return False


def _jsonable(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, np.generic):
            v = v.item()
        if isinstance(v, float) and np.isnan(v):
            v = None
        out[k] = v
    return out
