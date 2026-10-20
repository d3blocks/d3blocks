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

try:
    from .._shared import check_dark_mode, dark_mode_flag, normalize_steps, pair_in, ref_in, template_env
    from ..utils import resolve_color_background, set_logo, set_path, update_config, write_html_file
except ImportError:
    from _shared import check_dark_mode, dark_mode_flag, normalize_steps, pair_in, ref_in, template_env
    from utils import resolve_color_background, set_logo, set_path, update_config, write_html_file


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
    # Captioned walkthrough: None keeps the uncaptioned trace.
    config['steps'] = kwargs.get('steps', None)
    # GUI
    config['color_background'] = kwargs.get('color_background', None)
    config['dark_mode'] = check_dark_mode(kwargs.get('dark_mode', True))
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
    extra = np.array([EDGE_VARIANTS[v]['width'] for v in out['variant']], dtype=float)
    out['width'] = np.round(width + extra, 2)

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

    steps = normalize_steps(
        config.get('steps'),
        {
            'nodes': ref_in(node_properties, 'node'),
            'edges': pair_in(zip(df['source'], df['target']), 'edge'),
        },
        'flowgraph',
    )

    data = {
        'nodes': [_jsonable(p) for p in node_properties.values()],
        'edges': [_jsonable(r) for r in df.to_dict(orient='records')],
        'groups': [_jsonable(g) for g in groups.values()],
        'steps': steps,
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
        'darkMode': dark_mode_flag(config.get('dark_mode', True)),
        'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
        'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
        'SUPPORT': config.get('support') or '',
        'SAVE_BUTTON_START': '' if save_button else '<!--',
        'SAVE_BUTTON_STOP': '' if save_button else '-->',
        'LOGO_BASE64': config['logo_base64'],
    }

    html = template_env(__name__, __file__).get_template('flowgraph.html.j2').render(content)
    write_html_file(config, html, logger)
    if config.get('notebook'):
        return notebook_iframe(html, config)
    return html


def notebook_iframe(html, config):
    """Wrap the chart in an iframe for Jupyter.

    The chart page fills its window (fixed positioning, own body background) and
    uses fixed element ids, so it is isolated in an iframe instead of being
    injected into the notebook page. Size: figsize, else full width x 650 px.
    """
    width, height = (list(config.get('figsize') or [None, None]) + [None, None])[:2]
    width = '%dpx' % width if width else '100%'
    height = '%dpx' % height if height else '650px'
    # Wrapped in a div: IPython warns about HTML that starts with '<iframe'.
    return ('<div class="d3blocks-flowgraph"><iframe srcdoc="%s" title="%s" '
            'style="width:%s;height:%s;border:0;border-radius:6px" '
            'sandbox="allow-scripts allow-downloads allow-popups"></iframe></div>'
            % (html_escape(html, quote=True), html_escape(str(config.get('title', 'Flowgraph'))), width, height))


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


MERMAID_FILE_SUFFIXES = ('.md', '.markdown', '.mmd', '.mermaid')
FLOWCHART_KINDS = ('flowchart', 'graph', 'flowchart-elk')
STATE_KINDS = ('stateDiagram', 'stateDiagram-v2')
# Diagram keywords the flowgraph block reads.
MERMAID_KINDS = FLOWCHART_KINDS + STATE_KINDS


def is_mermaid_source(obj):
    """True for str / path-like input, which is read as Mermaid (see read_mermaid)."""
    return isinstance(obj, (str, os.PathLike))


def read_mermaid(source, logger=None, kinds=MERMAID_KINDS):
    """Return Mermaid diagram text from text, Markdown or a file path.

    Parameters
    ----------
    source : str or path-like
        * Mermaid diagram text.
        * Markdown text with ```mermaid fenced blocks.
        * Path to a .md / .markdown file (fenced blocks) or a .mmd / .mermaid file.
        From Markdown, the first fenced block whose diagram keyword is in `kinds`
        is used; other diagram types are skipped.
    kinds : tuple of str, (default: MERMAID_KINDS)
        Diagram keywords to accept, e.g. ('sequenceDiagram',). The default is what
        flowgraph reads: flowcharts ('flowchart', 'graph', 'flowchart-elk') and
        state diagrams ('stateDiagram', 'stateDiagram-v2').

    Returns
    -------
    str
        Mermaid diagram text.

    """
    path = _as_mermaid_path(source)
    text = path.read_text(encoding='utf-8') if path is not None else str(source)
    blocks = re.findall(r'^[ \t]*```+[ \t]*mermaid[^\n]*\n(.*?)^[ \t]*```', text, re.S | re.M)
    if not blocks:
        return text
    found = [b for b in blocks if _first_statement(b).split()[:1] in [[k] for k in kinds]]
    if not found:
        raise ValueError(
            'No Mermaid diagram of kind %s found in the ```mermaid blocks of %s.'
            % ('/'.join(kinds), path or 'the Markdown text')
        )
    if len(found) > 1 and logger is not None:
        logger.info('Found %d Mermaid diagrams of kind %s; using the first.' % (len(found), '/'.join(kinds)))
    return found[0]


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


# Every Mermaid parser in d3blocks (flowchart, stateDiagram, sequenceDiagram, erDiagram)
# follows one rule: a statement is understood, explicitly ignored, or a ValueError naming
# its line. Ignored everywhere: blank lines, %% comments, %%{init}%% directives and the
# accessibility metadata accTitle / accDescr, none of which change the diagram.
_ACC_LINE = re.compile(r'^acc(Title|Descr)\s*:')
_ACC_BLOCK = re.compile(r'^accDescr\s*\{')


def _mermaid_lines(text):
    """Yield (line number, statement) for the lines of Mermaid text that carry the diagram.

    Line numbers count from the first line of the diagram text (in Markdown: of the
    fenced block).
    """
    in_acc = False
    for lineno, raw in enumerate(str(text).splitlines(), 1):
        stmt = raw.strip()
        if in_acc:
            in_acc = '}' not in stmt
            continue
        if not stmt or stmt.startswith('%%') or _ACC_LINE.match(stmt):
            continue
        if _ACC_BLOCK.match(stmt):
            in_acc = '}' not in stmt
            continue
        yield lineno, stmt


def _mermaid_error(kind, lineno, stmt, supported):
    """The ValueError for a statement a Mermaid parser does not support."""
    return ValueError('Mermaid %s line %d is not supported: %r. Supported: %s.' % (kind, lineno, stmt, supported))


def from_mermaid(text, logger=None):
    """Convert a Mermaid flowchart or state diagram into Flowgraph inputs.

    Flowcharts: the 'flowchart'/'graph' header with direction, node shapes
    ([] () ([]) [[]] [()] (()) {} {{}} [//] [\\] >]), quoted labels and <br>,
    links (--> --- -.-> ==> ~~~ with |text| or inline text), chains (A --> B --> C),
    '&' (A & B --> C), nested subgraphs, node colours from 'style' and
    'classDef' + 'class' / ':::', and edge colours / dashes from 'linkStyle'.
    Comments, init directives and accTitle / accDescr are ignored. Anything else
    (click, per-subgraph direction, links to subgraphs, unparseable statements)
    raises a ValueError naming the line, as in every d3blocks Mermaid parser.

    State diagrams ('stateDiagram' / 'stateDiagram-v2'): see _from_mermaid_state.

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
    kind = _first_statement(text).split()[:1]
    if kind in [[k] for k in STATE_KINDS]:
        return _from_mermaid_state(text, logger=logger)
    if kind not in [[k] for k in FLOWCHART_KINDS]:
        raise ValueError(
            'Expected a Mermaid flowchart (%s) or state diagram (%s); the first statement is %r.'
            % ('/'.join(FLOWCHART_KINDS), '/'.join(STATE_KINDS), _first_statement(text))
        )
    nodes, groups, edges, classes = {}, {}, [], {}
    stack, direction, link_styles, group_line = [], None, [], {}

    def node(name, label=None, shape=None):
        n = nodes.setdefault(name, {})
        if label is not None:
            n['label'] = label
        if shape is not None:
            n['shape'] = shape
        if stack and 'group' not in n:
            n['group'] = stack[-1]
        return n

    def unsupported(lineno, stmt):
        return _mermaid_error('flowchart', lineno, stmt, _FLOWCHART_SUPPORTED)

    for lineno, line in _mermaid_lines(text):
        for stmt in _mermaid_split(line):
            stmt = stmt.strip()
            if not stmt:
                continue
            head = stmt.split()[0]
            if head in FLOWCHART_KINDS:
                parts = stmt.split()
                if len(parts) > 2 or (len(parts) == 2 and parts[1].upper() not in _MERMAID_DIRECTIONS):
                    raise unsupported(lineno, stmt)
                if len(parts) == 2:
                    direction = _MERMAID_DIRECTIONS[parts[1].upper()]
                continue
            if head == 'subgraph':
                gid, label = _mermaid_subgraph(stmt[len('subgraph') :].strip())
                groups[gid] = {'label': label, 'parent': stack[-1] if stack else None}
                group_line[gid] = lineno
                stack.append(gid)
                continue
            if stmt == 'end':
                if not stack:
                    raise ValueError('Mermaid flowchart line %d: "end" without an open "subgraph".' % lineno)
                stack.pop()
                continue
            if head == 'style':
                parts = stmt.split(None, 2)
                if len(parts) < 3:
                    raise unsupported(lineno, stmt)
                color = _mermaid_color(parts[2])
                if color:
                    node(parts[1])['color'] = color
                continue
            if head == 'classDef':
                parts = stmt.split(None, 2)
                if len(parts) < 3:
                    raise unsupported(lineno, stmt)
                for name in parts[1].split(','):
                    classes[name] = _mermaid_color(parts[2])
                continue
            if head == 'class':
                parts = stmt.split()
                if len(parts) != 3:
                    raise unsupported(lineno, stmt)
                for name in parts[1].split(','):
                    node(name)['class'] = parts[2]
                continue
            if head == 'linkStyle':
                link_styles.append((lineno, stmt))
                continue
            if head == 'click' or (head == 'direction' and len(stmt.split()) == 2):
                # Click handlers and per-subgraph directions have no equivalent here.
                raise unsupported(lineno, stmt)
            # All or nothing: nodes and edges of a statement are kept only if it parses.
            pending, chain_edges = [], []

            def record(name, label=None, shape=None):
                extra = {}
                pending.append((name, label, shape, extra))
                return extra

            try:
                _mermaid_chain(stmt, record, chain_edges)
            except ValueError as e:
                raise ValueError(
                    'Mermaid flowchart line %d could not be parsed: %r (%s). Supported: %s.'
                    % (lineno, stmt, e, _FLOWCHART_SUPPORTED)
                ) from None
            for name, label, shape, extra in pending:
                node(name, label, shape).update(extra)
            edges.extend([list(e) + [None, lineno] for e in chain_edges])
    if stack:
        raise ValueError('Mermaid flowchart line %d: subgraph %r has no "end".' % (group_line[stack[-1]], stack[-1]))

    for n in nodes.values():
        cls = n.pop('class', None)
        if cls and classes.get(cls) and 'color' not in n:
            n['color'] = classes[cls]

    for e in edges:
        for end in e[:2]:
            if end in groups:
                raise ValueError(
                    'Mermaid flowchart line %d: links to subgraphs are not supported (%r is a subgraph); '
                    'link to a node inside it instead.' % (e[-1], end)
                )

    _apply_link_styles(edges, link_styles)
    if not nodes:
        raise ValueError('No Mermaid flowchart nodes found. Expected text such as '
                         '"flowchart LR; A[Start] --> B{Valid?}", Markdown with a ```mermaid block, '
                         'or a path to a %s file.' % '/'.join(MERMAID_FILE_SUFFIXES))
    # Invisible links (~~~) only count for linkStyle numbering.
    rows = [e[:6] for e in edges if e[3] != 'invisible']
    df = pd.DataFrame(rows, columns=['source', 'target', 'label', 'style', 'weight', 'color'])
    if df['color'].isna().all():
        df = df.drop(columns='color')
    return df, nodes, groups, direction


_FLOWCHART_SUPPORTED = (
    'nodes and links (A[text] --> B, A -->|text| B, A & B --> C, chains), subgraph ... end, '
    'style, classDef, class, :::, linkStyle and %% comments'
)


def _apply_link_styles(edges, link_styles):
    """Apply 'linkStyle default|i,j stroke:#hex,stroke-dasharray:...' to the edge rows.

    Links are numbered from 0 in the order they are written, as in Mermaid (invisible
    ~~~ links included). Sets the edge colour (stroke) and a dashed style
    (stroke-dasharray); 'default' applies first, numbered links override it.
    """
    for lineno, stmt in sorted(link_styles, key=lambda x: x[1].split()[1:2] != ['default']):
        parts = stmt.split(None, 2)
        if len(parts) < 3:
            raise _mermaid_error('flowchart', lineno, stmt, _FLOWCHART_SUPPORTED)
        if parts[1] == 'default':
            idx = range(len(edges))
        else:
            try:
                idx = [int(i) for i in parts[1].split(',')]
            except ValueError:
                raise _mermaid_error('flowchart', lineno, stmt, _FLOWCHART_SUPPORTED) from None
            bad = [i for i in idx if not 0 <= i < len(edges)]
            if bad:
                raise ValueError(
                    'Mermaid flowchart line %d: linkStyle refers to link %d, but the diagram has %d '
                    'links (numbered from 0).' % (lineno, bad[0], len(edges))
                )
        props = _mermaid_props(parts[2])
        for i in idx:
            if props.get('stroke'):
                edges[i][5] = props['stroke']
            if props.get('stroke-dasharray'):
                edges[i][3] = 'dashed'


_STATE_REF = r'(\[\*\]|[A-Za-z0-9_]+)'
_STATE_TRANSITION = re.compile(r'^' + _STATE_REF + r'\s*-->\s*' + _STATE_REF + r'\s*(?::(.*))?$')
_STATE_NOTE = re.compile(r'^note\s+(?:left|right)\s+of\s+([A-Za-z0-9_]+)\s*(?::(.*))?$')


def _from_mermaid_state(text, logger=None):
    """Convert a Mermaid state diagram into Flowgraph inputs.

    Supported: transitions 'A --> B' and 'A --> B : label' (the label is everything
    after the first ':'), '[*]' as one start and one end pseudo-state (small circles),
    notes ('note right of A' ... 'end note', 'note left of A : text') which are added
    to the state's tooltip, a top-level 'direction LR|TB|...', 'classDef' + 'class'
    colours and '%%' comments. Other statements (composite states, <<choice>>,
    'state "x" as A', 'A : description', ...) raise a ValueError naming the line.

    Returns
    -------
    tuple
        (edges DataFrame, nodes dict, groups dict (empty), direction: the diagram's
        'direction' or 'TB')

    """
    nodes, edges, classes, direction = {}, [], {}, None
    note_for, note_lines, note_line = None, [], 0

    def unsupported(lineno, stmt):
        return _mermaid_error(
            'stateDiagram',
            lineno,
            stmt,
            'transitions (A --> B : label), [*] start/end, notes, direction, classDef/class and %% comments',
        )

    def state(name):
        return nodes.setdefault(name, {})

    def add_note(name, lines):
        n = state(name)
        # Tooltips may hold HTML, so the note text is escaped and its lines joined with <br>.
        note = '<br>'.join(html_escape(line) for line in lines)
        n['tooltip'] = n['tooltip'] + '<br>' + note if n.get('tooltip') else note

    for lineno, stmt in _mermaid_lines(text):
        if note_for is not None:
            if stmt == 'end note':
                add_note(note_for, note_lines)
                note_for = None
            else:
                note_lines.append(stmt)
            continue
        stmt = stmt.rstrip(';').rstrip()
        parts = stmt.split()
        head = parts[0]
        if head in STATE_KINDS and len(parts) == 1:
            continue
        if head == 'direction' and len(parts) == 2:
            if parts[1].upper() not in _MERMAID_DIRECTIONS:
                raise unsupported(lineno, stmt)
            direction = _MERMAID_DIRECTIONS[parts[1].upper()]
            continue
        if head == 'classDef':
            parts = stmt.split(None, 2)
            if len(parts) < 3:
                raise unsupported(lineno, stmt)
            for name in parts[1].split(','):
                classes[name] = _mermaid_color(parts[2])
            continue
        if head == 'class':
            if len(parts) != 3:
                raise unsupported(lineno, stmt)
            for name in parts[1].split(','):
                state(name)['class'] = parts[2]
            continue
        m = _STATE_NOTE.match(stmt)
        if m:
            if m.group(2) is not None:
                add_note(m.group(1), [m.group(2).strip()])
            else:
                note_for, note_lines, note_line = m.group(1), [], lineno
            continue
        m = _STATE_TRANSITION.match(stmt)
        if m:
            src = '__start__' if m.group(1) == '[*]' else m.group(1)
            tgt = '__end__' if m.group(2) == '[*]' else m.group(2)
            for name in (src, tgt):
                if name in ('__start__', '__end__'):
                    nodes.setdefault(
                        name, {'label': '', 'shape': 'circle', 'color': DEFAULT_EDGE_COLOR, 'tooltip': name.strip('_')}
                    )
                else:
                    state(name)
            edges.append((src, tgt, (m.group(3) or '').strip(), 'solid', 1))
            continue
        raise unsupported(lineno, stmt)
    if note_for is not None:
        raise ValueError('Mermaid stateDiagram line %d: note for %r has no "end note".' % (note_line, note_for))

    for n in nodes.values():
        cls = n.pop('class', None)
        if cls and classes.get(cls) and 'color' not in n:
            n['color'] = classes[cls]
    if not edges:
        raise ValueError(
            'No Mermaid state transitions found. Expected text such as '
            '"stateDiagram-v2\n  [*] --> pending\n  pending --> done : finish".'
        )
    df = pd.DataFrame(edges, columns=['source', 'target', 'label', 'style', 'weight'])
    return df, nodes, {}, direction or 'TB'


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


def _mermaid_split(line):
    """Split one line on ';' outside quotes, brackets and |edge labels|."""
    out, buf, depth, quoted, piped = [], '', 0, False, False
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


def _mermaid_props(spec):
    """'fill:#f00,stroke:#333;' -> {'fill': '#f00', 'stroke': '#333'}."""
    props = dict(p.split(':', 1) for p in spec.replace(';', ',').split(',') if ':' in p)
    return {k.strip(): v.strip() for k, v in props.items()}


def _mermaid_color(spec):
    props = _mermaid_props(spec)
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
        style = 'invisible' if '~' in arrow else 'dotted' if '.' in arrow else 'solid'
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
