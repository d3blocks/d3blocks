"""ERD block.

Entity-relationship diagrams: entities are table boxes with one row per column
(name, type and PK/FK/UK badges), relationships are lines with crow's-foot
cardinality markers. Laid out with dagre. Input is a Mermaid erDiagram or a
DataFrame of relationships.

Library     : d3blocks
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

import json
import re
from html import escape as html_escape

import numpy as np
import pandas as pd

try:
    from .._shared import (
        check_dark_mode,
        dark_mode_flag,
        normalize_steps,
        notebook_iframe,
        pair_in,
        ref_in,
        template_env,
    )
    from ..flowgraph import Flowgraph as fg
    from ..utils import resolve_color_background, set_logo, set_path, update_config, write_html_file
except ImportError:
    import flowgraph.Flowgraph as fg
    from _shared import check_dark_mode, dark_mode_flag, normalize_steps, notebook_iframe, pair_in, ref_in, template_env
    from utils import resolve_color_background, set_logo, set_path, update_config, write_html_file

CARDINALITIES = ('one', 'zero_or_one', 'one_or_more', 'zero_or_more')
KEYS = ('PK', 'FK', 'UK')
SHOW_COLUMNS = ('all', 'keys', 'none')
DIRECTIONS = fg.DIRECTIONS
DEFAULT_ENTITY_COLOR = '#A78BFA'

is_mermaid_source = fg.is_mermaid_source
merge_node_attributes = fg.merge_node_attributes


# %% Set configuration properties
def set_config(config={}, font={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] = 'erd'
    config['title'] = kwargs.get('title', 'ERD - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'erd.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['font'] = {**{'size': 12}, **font}
    direction = str(kwargs.get('direction', 'LR')).upper()
    config['direction'] = fg._check_choice(
        'TB' if direction == 'TD' else direction, DIRECTIONS, 'direction', 'LR', logger, upper=True
    )
    config['show_columns'] = fg._check_choice(
        kwargs.get('show_columns', 'all'), SHOW_COLUMNS, 'show_columns', 'all', logger
    )
    config['show_types'] = kwargs.get('show_types', True)
    config['nodesep'] = kwargs.get('nodesep', 50)
    config['ranksep'] = kwargs.get('ranksep', 90)
    # Captioned walkthrough: custom steps only.
    config['steps'] = kwargs.get('steps', None)
    # GUI
    config['color_background'] = kwargs.get('color_background', None)
    config['dark_mode'] = check_dark_mode(kwargs.get('dark_mode', True))
    config['save_button'] = kwargs.get('save_button', True)
    config['show_side_panel'] = kwargs.get('show_side_panel', True)
    config['show_top_panel'] = kwargs.get('show_top_panel', True)
    return config


# %% Entities
def set_node_properties(df, entities=None, logger=None, **kwargs):
    """Set the entity properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Relationships with at least the columns 'source' and 'target'.
    entities : pd.DataFrame or dict, (default: None)
        Per-entity attributes keyed by entity name: 'label', 'color', 'tooltip' and
        'columns', a list of {'name', 'type', 'key', 'comment'} where 'key' is '',
        'PK', 'FK', 'UK' or a comma list such as 'PK,FK'. A DataFrame may hold the name
        in a 'name' column or in its index. Listed entities come first; entities that
        only occur in `df` follow without columns.

    Returns
    -------
    dict
        {entity name: {'name', 'label', 'color', 'tooltip', 'columns'}}

    """
    fg._check_columns(df)
    attrs = fg._nodes_to_dict(entities)
    order = list(attrs)
    order += [n for n in pd.unique(df[['source', 'target']].astype(str).values.ravel()) if n not in attrs]
    props = {}
    for name in order:
        a = attrs.get(name, {})
        props[name] = {
            'name': name,
            'label': str(fg._get(a, 'label', name)),
            'color': fg._get(a, 'color', None) or DEFAULT_ENTITY_COLOR,
            'tooltip': fg._optional_str(fg._get(a, 'tooltip', None)),
            'columns': _columns(name, a.get('columns')),
        }
    return props


def _columns(entity, columns):
    """Normalize an entity's columns to [{'name', 'type', 'key', 'comment'}]."""
    if columns is None or (isinstance(columns, float) and np.isnan(columns)):
        return []
    out = []
    for i, c in enumerate(columns):
        if isinstance(c, str):
            c = {'name': c}
        if not isinstance(c, dict) or not c.get('name'):
            raise ValueError(
                "Entity %r column %d: expected {'name', 'type', 'key', 'comment'}; got %r." % (entity, i, c)
            )
        keys = [k.strip().upper() for k in str(c.get('key') or '').split(',') if k.strip()]
        bad = [k for k in keys if k not in KEYS]
        if bad:
            raise ValueError('Entity %r column %r: unknown key(s) %s; use %s.' % (entity, c['name'], bad, KEYS))
        out.append(
            {
                'name': str(c['name']),
                'type': str(c.get('type') or ''),
                'key': ','.join(keys),
                'comment': str(c.get('comment') or ''),
            }
        )
    return out


# %% Relationships
def set_edge_properties(df, logger=None, **kwargs):
    """Set the relationship properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Required columns: 'source', 'target'.
        Optional columns:
            * 'source_card', 'target_card': 'one', 'zero_or_one', 'one_or_more' or
              'zero_or_more' (crow's-foot marker at that end). Missing: no marker.
            * 'label': relationship text.
            * 'identifying': True (solid line, default) or False (dashed).

    Returns
    -------
    pd.DataFrame
        One row per relationship with the columns source, target, source_card,
        target_card, label and identifying.

    """
    fg._check_columns(df)
    out = pd.DataFrame(
        {
            'source': df['source'].astype(str).values,
            'target': df['target'].astype(str).values,
        }
    )
    for col in ('source_card', 'target_card'):
        cards = fg._column(df, col, None).astype(object)
        cards = cards.where(cards.notna(), None).map(lambda v: None if v is None else str(v).lower())
        fg._warn_unknown(cards.dropna(), CARDINALITIES, col, 'no marker', logger)
        out[col] = cards.where(cards.isin(CARDINALITIES), None).values
    out['label'] = fg._column(df, 'label', '').fillna('').astype(str).values
    out['identifying'] = [_as_bool(v) for v in fg._column(df, 'identifying', True)]
    return out


def _as_bool(v):
    """'identifying' as bool; missing is True, and text such as 'false' or 'no' is False."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return True
    if isinstance(v, str):
        return v.strip().lower() not in ('false', 'f', 'no', 'n', '0', '')
    return bool(v)


# %% Show
def show(df, **kwargs):
    """Build and show the diagram.

    Parameters
    ----------
    df : pd.DataFrame()
        Relationship properties (output of set_edge_properties).
    config : dict
        Configuration keys.
    node_properties : dict or pd.DataFrame
        Entity properties (output of set_node_properties).

    Returns
    -------
    str
        The generated HTML.

    """
    logger = kwargs.get('logger', None)
    entities = fg._node_properties_to_dict(kwargs.get('node_properties'))
    config = update_config(kwargs, logger).copy()

    # Relationships may reference entities that were added after set_node_properties().
    for name in pd.unique(df[['source', 'target']].values.ravel()):
        if name not in entities:
            entities[name] = {
                'name': name,
                'label': name,
                'color': DEFAULT_ENTITY_COLOR,
                'tooltip': None,
                'columns': [],
            }
    for e in entities.values():
        e['columns'] = _columns(e['name'], e.get('columns'))

    steps = normalize_steps(
        config.get('steps'),
        {
            'nodes': ref_in(entities, 'entity'),
            'edges': pair_in(zip(df['source'], df['target']), 'relationship', undirected=True),
        },
        'erd',
    )

    data = {
        'entities': [fg._jsonable(e) for e in entities.values()],
        'relationships': [fg._jsonable(r) for r in df.to_dict(orient='records')],
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
        JSON string with entities, relationships and steps.
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
        'showColumns': config['show_columns'],
        'showTypes': bool(config['show_types']),
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
        'darkMode': dark_mode_flag(config.get('dark_mode', True)),
        'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
        'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
        'SUPPORT': config.get('support') or '',
        'SAVE_BUTTON_START': '' if save_button else '<!--',
        'SAVE_BUTTON_STOP': '' if save_button else '-->',
        'LOGO_BASE64': config['logo_base64'],
    }
    html = template_env(__name__, __file__).get_template('erd.html.j2').render(content)
    write_html_file(config, html, logger)
    if config.get('notebook'):
        return notebook_iframe(html, config, 'erd')
    return html


# %% Mermaid
_NAME = r'([A-Za-z0-9_][A-Za-z0-9_.-]*)'
_RELATIONSHIP = re.compile(r'^' + _NAME + r'\s*([|}o]{2})(--|\.\.)([|{o]{2})\s*' + _NAME + r'\s*(?::\s*(.*))?$')
_ENTITY_OPEN = re.compile(r'^' + _NAME + r'\s*\{$')
_COLUMN = re.compile(r'^(\S+)\s+(\S+)((?:\s+(?:PK|FK|UK)(?:\s*,\s*(?:PK|FK|UK))*)?)(?:\s+"([^"]*)")?$')
# Mermaid cardinality markers per end (both spellings of the asymmetric ones).
_LEFT_CARDS = {'||': 'one', '|o': 'zero_or_one', 'o|': 'zero_or_one', '}|': 'one_or_more', '}o': 'zero_or_more'}
_RIGHT_CARDS = {'||': 'one', 'o|': 'zero_or_one', '|o': 'zero_or_one', '|{': 'one_or_more', 'o{': 'zero_or_more'}


def from_mermaid(text, logger=None):
    """Convert a Mermaid erDiagram into Erd inputs.

    Supported: relationships 'A ||--o{ B : label' with all four markers per end
    (|| |o/o| }|/|{ }o/o{), '--' (identifying, solid) and '..' (non-identifying,
    dashed); entity blocks 'A { type name PK "comment" }' with keys PK, FK, UK and
    comma lists ('PK,FK'); entities that only occur in relationships; a top-level
    'direction LR|TB|...'; '%%' comments (accTitle / accDescr are ignored too). Other
    statements raise a ValueError naming the line.

    Parameters
    ----------
    text : str or path-like
        Mermaid text, Markdown with a ```mermaid block, or a path to a .md / .markdown /
        .mmd / .mermaid file. From Markdown, the first erDiagram block is used.

    Returns
    -------
    tuple
        (relationships DataFrame, entities dict, direction or None)

    """
    text = fg.read_mermaid(text, logger=logger, kinds=('erDiagram',))
    if fg._first_statement(text).split()[:1] != ['erDiagram']:
        raise ValueError('Expected a Mermaid erDiagram; the first statement is %r.' % fg._first_statement(text))
    entities, rels, current, current_line, direction = {}, [], None, 0, None
    supported = (
        'relationships (A ||--o{ B : label), entity blocks (A { type name PK "comment" }), direction and %% comments'
    )

    for lineno, stmt in fg._mermaid_lines(text):
        if current is not None:
            if stmt == '}':
                current = None
                continue
            m = _COLUMN.match(stmt)
            if not m:
                raise ValueError(
                    'Mermaid erDiagram line %d: unsupported column %r in entity %r. Expected '
                    '\'type name [PK|FK|UK] ["comment"]\'.' % (lineno, stmt, current)
                )
            keys = ','.join(k.strip() for k in m.group(3).split(',') if k.strip())
            entities[current]['columns'].append(
                {'name': m.group(2), 'type': m.group(1), 'key': keys, 'comment': m.group(4) or ''}
            )
            continue
        if stmt == 'erDiagram':
            continue
        parts = stmt.split()
        if parts[0] == 'direction' and len(parts) == 2:
            if parts[1].upper() not in fg._MERMAID_DIRECTIONS:
                raise fg._mermaid_error('erDiagram', lineno, stmt, supported)
            direction = fg._MERMAID_DIRECTIONS[parts[1].upper()]
            continue
        m = _ENTITY_OPEN.match(stmt)
        if m:
            current, current_line = m.group(1), lineno
            entities.setdefault(current, {}).setdefault('columns', [])
            continue
        m = _RELATIONSHIP.match(stmt)
        if m:
            left, line, right = m.group(2), m.group(3), m.group(4)
            if left not in _LEFT_CARDS or right not in _RIGHT_CARDS:
                raise ValueError(
                    'Mermaid erDiagram line %d: unknown cardinality %r in %r.' % (lineno, left + line + right, stmt)
                )
            source, target = m.group(1), m.group(5)
            entities.setdefault(source, {})
            entities.setdefault(target, {})
            label = (m.group(6) or '').strip()
            if len(label) >= 2 and label[0] == label[-1] == '"':
                label = label[1:-1]
            rels.append((source, target, _LEFT_CARDS[left], _RIGHT_CARDS[right], label, line == '--'))
            continue
        raise fg._mermaid_error('erDiagram', lineno, stmt, supported)
    if current is not None:
        raise ValueError('Mermaid erDiagram line %d: entity %r has no closing "}".' % (current_line, current))
    if not entities:
        raise ValueError(
            'No Mermaid erDiagram entities found. Expected text such as "erDiagram\\n  CUSTOMER ||--o{ ORDER : places".'
        )
    df = pd.DataFrame(rels, columns=['source', 'target', 'source_card', 'target_card', 'label', 'identifying'])
    return df, entities, direction
