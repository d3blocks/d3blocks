"""Maps block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from jinja2 import Environment, PackageLoader
import numpy as np
import colourmap as cm
import os
import json
import difflib

try:
    from .. utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script
except Exception:
    from utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script


# Common aliases → GeoJSON feature names (world.geojson uses short forms like "USA")
_COUNTRY_ALIASES = {
    'united states': 'USA',
    'united states of america': 'USA',
    'us': 'USA',
    'u.s.': 'USA',
    'u.s.a.': 'USA',
    'america': 'USA',
    'uk': 'England',
    'u.k.': 'England',
    'united kingdom': 'England',
    'great britain': 'England',
    'britain': 'England',
    'holland': 'Netherlands',
    'the netherlands': 'Netherlands',
    'russian federation': 'Russia',
    'south korea': 'Korea',
    'north korea': 'North Korea',
    'tanzania': 'United Republic of Tanzania',
    'czech republic': 'Czechia',
    'ivory coast': "Côte d'Ivoire",
    "cote d'ivoire": "Côte d'Ivoire",
}


def _geojson_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'd3js', 'world.geojson')


def list_country_names(map_name='world'):
    """Return official country names available for the given map.

    Parameters
    ----------
    map_name : str, optional
        Map identifier. Currently only ``'world'`` is supported (GeoJSON).

    Returns
    -------
    list of str
        Sorted country / region names from the map geometry.
    """
    map_name = (map_name or 'world').lower()
    if map_name != 'world':
        raise ValueError(
            "Only map_name='world' is supported for now. "
            "Regional maps (e.g. 'netherlands') will be added later."
        )
    path = _geojson_path()
    with open(path, 'r', encoding='utf-8') as f:
        geo = json.load(f)
    names = sorted({
        feat.get('properties', {}).get('name')
        for feat in geo.get('features', [])
        if feat.get('properties', {}).get('name')
    })
    return names


def match_country_names(names, map_name='world', cutoff=0.8, logger=None):
    """Fuzzy-match requested names to official map feature names.

    Parameters
    ----------
    names : list of str
        User-provided country / region names.
    map_name : str, optional
        Map identifier (default ``'world'``).
    cutoff : float, optional
        difflib match threshold in [0, 1].
    logger : optional
        Logger for warnings.

    Returns
    -------
    matched : list of str or None
        Official name per input (None if unmatched).
    report : dict
        ``{'matched': [(input, official), ...], 'unmatched': [input, ...]}``
    """
    official = list_country_names(map_name=map_name)
    official_lower = {n.lower(): n for n in official}
    matched = []
    report = {'matched': [], 'unmatched': []}

    for raw in names:
        if raw is None or (isinstance(raw, float) and np.isnan(raw)):
            matched.append(None)
            report['unmatched'].append(raw)
            continue
        key = str(raw).strip()
        low = key.lower()

        # 1) alias table
        if low in _COUNTRY_ALIASES:
            alias_target = _COUNTRY_ALIASES[low]
            if alias_target.lower() in official_lower:
                official_name = official_lower[alias_target.lower()]
                matched.append(official_name)
                report['matched'].append((key, official_name))
                continue

        # 2) exact (case-insensitive)
        if low in official_lower:
            official_name = official_lower[low]
            matched.append(official_name)
            report['matched'].append((key, official_name))
            continue

        # 3) fuzzy
        hits = difflib.get_close_matches(key, official, n=1, cutoff=cutoff)
        if not hits:
            hits = difflib.get_close_matches(low, list(official_lower.keys()), n=1, cutoff=cutoff)
            if hits:
                hits = [official_lower[hits[0]]]
        if hits:
            matched.append(hits[0])
            report['matched'].append((key, hits[0]))
        else:
            matched.append(None)
            report['unmatched'].append(key)
            if logger is not None:
                logger.warning('Country name not found on map: %s' % key)
            else:
                print('[maps] Country name not found on map: %s' % key)

    return matched, report


def countries_from_names(country_names,
                         colors=None,
                         opacity=None,
                         values=None,
                         cmap='Set2',
                         map_name='world',
                         world_color='#D3D3D3',
                         world_opacity=0.6,
                         linewidth=1,
                         line='none',
                         stroke='#5A5A5A',
                         logger=None):
    """Build a countries dict (worldmap-style) from names + optional colors/values.

    Parameters
    ----------
    country_names : list of str
        Countries / regions to color.
    colors : list of str or None
        Hex colors or category labels (mapped via ``cmap``). Same length as names.
        If None, colors are generated from ``cmap``.
    opacity : float, list of float, or None
        Opacity per country. If None and ``values`` is set, opacity is scaled
        from values into (0.25, 1]. If both None, default 0.85.
    values : list of float or None
        Numeric values for sequential opacity (and optionally sequential color).
    cmap : str
        Colormap when colors must be generated.
    map_name : str
        Currently only ``'world'``.
    world_color, world_opacity, linewidth, line, stroke :
        Defaults for the World base layer and per-country borders.

    Returns
    -------
    dict
        ``{'World': {...}, 'Netherlands': {...}, ...}`` suitable for
        ``set_edge_properties``.
    """
    country_names = list(country_names) if country_names is not None else []
    n = len(country_names)
    matched, report = match_country_names(country_names, map_name=map_name, logger=logger)

    # Colors
    if colors is None:
        if values is not None:
            vals = np.asarray(values, dtype=float)
            # sequential: map values → colors via colourmap
            try:
                color_list = list(cm.fromlist(vals, cmap=cmap, scheme='hex', verbose=0)[0])
            except Exception:
                color_list = list(cm.generate(n, cmap=cmap, scheme='hex', verbose=0))
        else:
            try:
                color_list = list(cm.generate(n, cmap=cmap, scheme='hex', verbose=0))
            except Exception:
                color_list = list(cm.fromlist([str(i) for i in range(n)], cmap=cmap, scheme='hex', verbose=0)[0])
    else:
        colors = list(colors)
        if len(colors) == 1 and n > 1:
            colors = colors * n
        if len(colors) != n:
            raise ValueError('colors length (%d) must match country_names (%d)' % (len(colors), n))
        if np.all([cm.is_hex_color(c, verbose=0) for c in colors]):
            color_list = [str(c) for c in colors]
        else:
            color_list = list(cm.fromlist(np.asarray(colors).astype(str), cmap=cmap, scheme='hex', verbose=0)[0])

    # Opacity
    if opacity is None and values is not None:
        vals = np.asarray(values, dtype=float)
        vmin, vmax = np.nanmin(vals), np.nanmax(vals)
        if vmax > vmin:
            opacity_list = list(0.25 + 0.75 * (vals - vmin) / (vmax - vmin))
        else:
            opacity_list = [0.85] * n
    elif opacity is None:
        opacity_list = [0.85] * n
    elif isinstance(opacity, (int, float)):
        opacity_list = [float(opacity)] * n
    else:
        opacity_list = list(opacity)
        if len(opacity_list) != n:
            raise ValueError('opacity length must match country_names')

    countries = {
        'World': {
            'name': 'World',
            'color': world_color,
            'opacity': world_opacity,
            'line': line,
            'linewidth': linewidth,
            'stroke': stroke,
        }
    }

    for i, official in enumerate(matched):
        if official is None:
            continue
        # Later entries overwrite earlier if duplicate matches
        countries[official] = {
            'name': official,
            'color': str(color_list[i]),
            'opacity': float(opacity_list[i]),
            'line': line,
            'linewidth': linewidth,
            'stroke': stroke,
        }

    if logger is not None:
        logger.info('Colored %d countries (%d unmatched).' % (
            len(report['matched']), len(report['unmatched'])))
    return countries


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] = 'maps'
    config['title'] = kwargs.get('title', 'Maps - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'maps.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    if config['figsize'] is None:
        config['figsize'] = [None, None]
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['save_button'] = kwargs.get('save_button', True)
    config['show_controls'] = kwargs.get('show_controls', True)
    config['dark_mode'] = kwargs.get('dark_mode', True)
    config['map_name'] = kwargs.get('map_name', 'world')
    return config


# %% Set Edge properties
def set_edge_properties(X=None, **kwargs):
    """Set country (edge) properties for the map.

    Parameters
    ----------
    X : dict or None
        Country styling dict. Keys are country names; values are dicts with
        ``color``, ``opacity``, ``line``, ``linewidth``, ``stroke``.
        Must include or will auto-create a ``World`` entry for the base layer.
        Ignored when ``country_names`` is provided in kwargs.
    country_names : list of str, optional
        Worldmap-style input: names to color (fuzzy-matched to the map).
    country_colors, country_opacity, country_values : optional
        Passed to ``countries_from_names``.
    cmap, map_name, logger : optional

    Returns
    -------
    df : pd.DataFrame
        Country properties for the front-end.
    """
    logger = kwargs.get('logger', None)
    cmap = kwargs.get('cmap', 'Set2')
    map_name = kwargs.get('map_name', 'world')
    country_names = kwargs.get('country_names', None)

    default_world = {
        'name': 'World',
        'color': '#D3D3D3',
        'opacity': 0.6,
        'line': 'none',
        'linewidth': 0.5,
        'stroke': '#5A5A5A',
    }

    if country_names is not None:
        X = countries_from_names(
            country_names,
            colors=kwargs.get('country_colors', None),
            opacity=kwargs.get('country_opacity', None),
            values=kwargs.get('country_values', None),
            cmap=cmap,
            map_name=map_name,
            logger=logger,
        )

    if X is None:
        X = {}
    if not isinstance(X, dict):
        raise TypeError('countries / edge properties must be a dict')

    # Ensure World defaults
    if 'World' not in X or X.get('World') is None:
        X['World'] = dict(default_world)
    else:
        X['World'] = {**default_world, **X['World'], 'name': 'World'}

    countries = {}
    countries['World'] = X['World']
    for key in X.keys():
        if key == 'World':
            continue
        props = X[key] if isinstance(X[key], dict) else {}
        countries[key] = {
            'name': key,
            'color': props.get('color', X['World']['color']),
            'opacity': props.get('opacity', 0.85),
            'linewidth': props.get('linewidth', X['World'].get('linewidth', 1)),
            'line': props.get('line', X['World'].get('line', 'none')),
            'stroke': props.get('stroke', X['World'].get('stroke', '#5A5A5A')),
        }

    df = convert_dataframe_dict(countries, frame=True, logger=logger)
    return df


def set_node_properties(df=None, **kwargs):
    """Set marker (node) properties.

    Parameters
    ----------
    df : pd.DataFrame or None
        Columns: lon, lat, and optionally label, size, opacity, color.
        None or empty → no markers (country-only map).

    Returns
    -------
    dict_labels : dict
        Marker properties keyed by index.
    """
    logger = kwargs.get('logger', None)
    cmap = kwargs.get('cmap', 'Set1')

    if df is None:
        return {}
    # Empty frame
    if hasattr(df, 'empty') and df.empty:
        return {}
    if hasattr(df, 'shape') and df.shape[0] == 0:
        return {}

    # Get longitude
    lon = df.get('lon', None) if hasattr(df, 'get') else None
    if lon is None:
        lon = kwargs.get('lon')
    # Get latitude
    lat = df.get('lat', None) if hasattr(df, 'get') else None
    if lat is None:
        lat = kwargs.get('lat')

    if lon is None or lat is None:
        if logger is not None:
            logger.warning('No lon/lat for markers; drawing countries only.')
        return {}

    n = len(lon)

    # Get size
    size = df.get('size', None) if hasattr(df, 'get') else None
    if size is None:
        size = kwargs.get('size', None)
    if size is None:
        size = np.repeat(10, n)
    if isinstance(size, (int, float)):
        size = [size] * n

    # Get opacity
    opacity = df.get('opacity', None) if hasattr(df, 'get') else None
    if opacity is None:
        opacity = kwargs.get('opacity', None)
    if opacity is None:
        opacity = np.repeat([0.8], n)
    if isinstance(opacity, (int, float)):
        opacity = [opacity] * n

    # Get color
    color = df.get('color', None) if hasattr(df, 'get') else None
    if color is None:
        color = kwargs.get('color', None)
    if color is None:
        color = np.repeat(['#0981D1'], n)
    if isinstance(color, str) and cm.is_hex_color(color, verbose=0):
        color = [color] * n
    if isinstance(color, (np.ndarray, list)) and not np.all(list(map(lambda c: cm.is_hex_color(c, verbose=0), color))):
        color = cm.fromlist(np.asarray(color).astype(str), cmap=cmap, scheme='hex')[0]

    # Get label
    label = df.get('label', None) if hasattr(df, 'get') else None
    if label is None:
        label = kwargs.get('label', None)
    if label is None:
        label = np.repeat([''], n)
    if isinstance(label, (int, float, str)):
        label = [label] * n

    dict_labels = {}
    for i in np.arange(0, n):
        dict_labels[i] = {
            'lon': lon[i],
            'lat': lat[i],
            'label': label[i],
            'size': size[i],
            'color': color[i],
            'opacity': opacity[i],
        }
    return dict_labels


def show(countries, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    countries : DataFrame or dict
        Country properties.
    config : dict
        Configuration keys.
    node_properties : dict
        Marker properties (may be empty for country-only plots).

    Returns
    -------
    html : str
        Generated HTML.
    """
    node_properties = kwargs.get('node_properties', None)
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert node properties to dict (markers). Empty DataFrame/dict → no markers.
    if node_properties is None:
        node_properties = {}
    node_properties = convert_dataframe_dict(node_properties, frame=False, chart=config['chart'])
    def _is_empty_nodes(obj):
        if obj is None:
            return True
        if isinstance(obj, dict):
            return len(obj) == 0
        if hasattr(obj, 'empty'):
            return bool(obj.empty)
        try:
            return len(obj) == 0
        except TypeError:
            return False
    if _is_empty_nodes(node_properties):
        json_data = '[]'
    else:
        json_data = convert_to_json_format(node_properties, logger=logger)

    # Edge properties: Transform dataframe into input form for d3
    countries = convert_dataframe_dict(countries.copy(), frame=True)
    countries.reset_index(inplace=True, drop=True)
    json_countries = convert_to_json_format(countries, logger=logger)

    return write_html(json_countries, json_data, config, logger)


def write_html(json_countries, json_data, config, logger=None):
    """Write html."""
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])
    width = 'window.screen.width' if config['figsize'][0] is None else config['figsize'][0]
    height = 'window.screen.height' if config['figsize'][1] is None else config['figsize'][1]

    content = {
        'json_countries': json_countries,
        'json_data': json_data,
        'TITLE': config['title'],
        'WIDTH': width,
        'HEIGHT': height,
        'SUPPORT': config.get('support') or '',
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
        'show_controls': config.get('show_controls', True),
        'dark_mode': config.get('dark_mode', True),
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except Exception:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.maps', package_path='d3js'))

    index_template = jinja_env.get_template('maps.html.j2')
    html = index_template.render(content)
    write_html_file(config, html, logger)
    return html
