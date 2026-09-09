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
    from .. utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script, set_logo
except Exception:
    from utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script, set_logo


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


# Built-in short aliases (ISO and common names). Full catalog is discovered
# from maps/d3js/geo/*.geojson + iso_to_map.json.
_MAP_NAME_ALIASES = {
    'world': 'world',
    'nl': 'netherlands',
    'holland': 'netherlands',
    'the netherlands': 'netherlands',
    'us': 'united states of america',
    'usa': 'united states of america',
    'united states': 'united states of america',
    'uk': 'united kingdom',
    'gb': 'united kingdom',
    'great britain': 'united kingdom',
    'england': 'united kingdom',
    'britain': 'united kingdom',
}


# Regional admin-1 geometries (downloaded once, then cached on disk)
GEO_ZIP_URL = 'https://github.com/d3blocks/geojson/raw/refs/heads/main/geojson.zip'


def _d3js_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'd3js')


def _geo_dir():
    return os.path.join(_d3js_dir(), 'geo')


def _geo_zip_path():
    return os.path.join(_d3js_dir(), 'geojson.zip')


def _geo_data_ready():
    """True if regional geo files are already present on disk."""
    geo_dir = _geo_dir()
    marker = os.path.join(geo_dir, 'iso_to_map.json')
    if not os.path.isfile(marker):
        return False
    try:
        for fn in os.listdir(geo_dir):
            if fn.endswith('.geojson'):
                return True
    except OSError:
        return False
    return False


def download_geo_data(url=None, force=False, logger=None):
    """Download and extract regional GeoJSON archive if missing.

    Parameters
    ----------
    url : str, optional
        Zip URL. Default: ``GEO_ZIP_URL`` (d3blocks/geojson).
    force : bool, optional
        Re-download and re-extract even when files already exist.
    logger : optional
        Logger for status messages.

    Returns
    -------
    str
        Path to the extracted ``d3js/geo`` directory.
    """
    import urllib.request
    import zipfile

    url = url or GEO_ZIP_URL
    geo_dir = _geo_dir()
    zip_path = _geo_zip_path()
    d3js = _d3js_dir()

    if not force and _geo_data_ready():
        if logger is not None:
            logger.info('Geo data already present: %s' % geo_dir)
        return geo_dir

    os.makedirs(d3js, exist_ok=True)

    # Download zip only if missing (unless force)
    if force or not os.path.isfile(zip_path):
        msg = 'Downloading geo data from %s' % url
        if logger is not None:
            logger.info(msg)
        else:
            print('[maps] ' + msg)
        try:
            urllib.request.urlretrieve(url, zip_path)
        except Exception as e:
            raise RuntimeError(
                'Failed to download geo data from %s (%s). '
                'Place geojson files under %s manually.' % (url, e, geo_dir)
            ) from e
    else:
        if logger is not None:
            logger.info('Using cached zip: %s' % zip_path)

    if not os.path.isfile(zip_path):
        raise FileNotFoundError('Geo zip not found: %s' % zip_path)

    if logger is not None:
        logger.info('Extracting geo data to %s' % d3js)
    else:
        print('[maps] Extracting geo data…')

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Archive layout: geo/*.geojson, geo/iso_to_map.json → d3js/geo/
        zf.extractall(d3js)

    if not _geo_data_ready():
        raise RuntimeError(
            'Geo data extract finished but %s is incomplete. '
            'Check the zip structure (expected geo/*.geojson).' % geo_dir
        )

    if logger is not None:
        n = sum(1 for fn in os.listdir(geo_dir) if fn.endswith('.geojson'))
        logger.info('Geo data ready: %d regional maps in %s' % (n, geo_dir))
    return geo_dir


def ensure_geo_data(logger=None):
    """Ensure regional geo files exist; download+extract once if needed."""
    return download_geo_data(force=False, logger=logger)


def _load_iso_map():
    """ISO-3166-1 alpha-2 → map_name from extracted admin-1 files."""
    ensure_geo_data()
    path = os.path.join(_geo_dir(), 'iso_to_map.json')
    if not os.path.isfile(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _discover_map_names():
    """Scan d3js/geo for regional map names. Always includes 'world'."""
    ensure_geo_data()
    names = ['world']
    geo_dir = _geo_dir()
    if os.path.isdir(geo_dir):
        try:
            for fn in sorted(os.listdir(geo_dir)):
                if fn.endswith('.geojson'):
                    names.append(fn[:-8].replace('_', ' '))
        except OSError:
            pass
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def list_map_names():
    """Return available map names (world + every regional admin-1 map)."""
    return _discover_map_names()


def normalize_map_name(map_name='world'):
    """Normalize user map_name / ISO code to a canonical key.

    Accepts full names (``'netherlands'``), ISO codes (``'NL'``), and a few
    short aliases (``'usa'``, ``'uk'``).
    """
    key = (map_name or 'world').strip().lower()
    if key == 'world':
        return 'world'

    # Built-in aliases
    if key in _MAP_NAME_ALIASES:
        key = _MAP_NAME_ALIASES[key]
        if key == 'world':
            return 'world'

    # Discover maps from disk (inline — avoids NameError if module partially reloaded)
    known = _discover_map_names()
    known_lower = {n.lower(): n for n in known}

    # Exact
    if key in known_lower:
        return known_lower[key]

    # ISO-2 code (e.g. 'DE', 'fr')
    iso_map = _load_iso_map()
    iso_key = key.upper()
    if iso_key in iso_map:
        return iso_map[iso_key]

    # Underscore form of file stem
    stem = key.replace(' ', '_')
    for n in known:
        if n.replace(' ', '_') == stem:
            return n

    # Fuzzy against known map names
    hits = difflib.get_close_matches(key, list(known_lower.keys()), n=1, cutoff=0.75)
    if hits:
        return known_lower[hits[0]]

    raise ValueError(
        "Unknown map_name=%r. Use Maps.list_map_names() to see all %d maps, "
        "or pass an ISO code like 'NL', 'US', 'DE'." % (map_name, len(known))
    )


def _geojson_path(map_name='world'):
    """Return filesystem path to the GeoJSON for map_name."""
    name = normalize_map_name(map_name)
    d3js = _d3js_dir()
    if name == 'world':
        path = os.path.join(d3js, 'world.geojson')
    else:
        ensure_geo_data()
        fname = name.replace(' ', '_') + '.geojson'
        path = os.path.join(d3js, 'geo', fname)
    if not os.path.isfile(path):
        raise FileNotFoundError('GeoJSON not found for map_name=%r (%s)' % (map_name, path))
    return path


def _geom_coords(geom):
    """Yield all coordinate pairs from a GeoJSON geometry."""
    if geom is None:
        return
    gtype = geom.get('type')
    coords = geom.get('coordinates')
    if not gtype or coords is None:
        return
    if gtype == 'Point':
        yield coords[0], coords[1]
    elif gtype in ('MultiPoint', 'LineString'):
        for c in coords:
            yield c[0], c[1]
    elif gtype in ('MultiLineString', 'Polygon'):
        for ring in coords:
            for c in ring:
                yield c[0], c[1]
    elif gtype == 'MultiPolygon':
        for poly in coords:
            for ring in poly:
                for c in ring:
                    yield c[0], c[1]
    elif gtype == 'GeometryCollection':
        for g in geom.get('geometries') or []:
            for xy in _geom_coords(g):
                yield xy


def _feature_centroid(feat):
    """Rough geographic centroid (mean of coordinates)."""
    xs, ys = [], []
    for x, y in _geom_coords(feat.get('geometry') or {}):
        xs.append(x)
        ys.append(y)
    if not xs:
        return None
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _haversine_km(a, b):
    """Great-circle distance in km between (lon, lat) pairs."""
    lon1, lat1 = a
    lon2, lat2 = b
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    h = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return float(2 * r * np.arcsin(np.sqrt(min(1.0, h))))


def filter_main_landmass(features, gap_km=1200.0, logger=None):
    """Keep the main contiguous region cluster; drop distant overseas parts.

    Builds a graph of features whose centroids are within ``gap_km``, then
    keeps the connected component with the most members (ties → more
    coordinate mass). This removes e.g. Caribbean islands from the
    Netherlands view so ``fitExtent`` zooms to the European mainland.

    Parameters
    ----------
    features : list of GeoJSON Feature
    gap_km : float
        Max centroid distance to treat two regions as connected.
    logger : optional

    Returns
    -------
    list of Feature
    """
    if not features or len(features) <= 1:
        return features

    centroids = [_feature_centroid(f) for f in features]
    valid = [i for i, c in enumerate(centroids) if c is not None]
    if len(valid) <= 1:
        return features

    # Adjacency by centroid distance
    neighbors = {i: [] for i in valid}
    for ai, i in enumerate(valid):
        for j in valid[ai + 1:]:
            if _haversine_km(centroids[i], centroids[j]) <= gap_km:
                neighbors[i].append(j)
                neighbors[j].append(i)

    # Seed = region with most neighbors (mainland density), not largest area
    # (Alaska would otherwise dominate the US).
    seed = max(valid, key=lambda i: (len(neighbors[i]), len(list(_geom_coords(features[i].get('geometry') or {})))))

    # BFS connected component
    cluster = set()
    stack = [seed]
    while stack:
        i = stack.pop()
        if i in cluster:
            continue
        cluster.add(i)
        stack.extend(neighbors[i])

    kept = [features[i] for i in sorted(cluster)]
    dropped = len(features) - len(kept)
    if dropped and logger is not None:
        dropped_names = [
            features[i].get('properties', {}).get('name', '?')
            for i in range(len(features)) if i not in cluster
        ]
        logger.info(
            'Excluded %d overseas/distant region(s) from map fit: %s'
            % (dropped, ', '.join(dropped_names[:12]) + ('…' if dropped > 12 else ''))
        )
    return kept


def load_geojson(map_name='world', include_overseas=False, gap_km=1200.0, logger=None):
    """Load FeatureCollection for the given map.

    Parameters
    ----------
    map_name : str
        World or regional map key / ISO code.
    include_overseas : bool, optional
        If False (default for regional maps), drop regions that are far from
        the main landmass cluster (e.g. Bonaire when mapping the Netherlands).
        Ignored for ``map_name='world'``.
    gap_km : float, optional
        Distance threshold for the main-landmass cluster.
    logger : optional
    """
    with open(_geojson_path(map_name), 'r', encoding='utf-8') as f:
        geo = json.load(f)

    name = normalize_map_name(map_name)
    if name != 'world' and not include_overseas:
        feats = geo.get('features') or []
        filtered = filter_main_landmass(feats, gap_km=gap_km, logger=logger)
        if len(filtered) < len(feats):
            geo = {'type': 'FeatureCollection', 'features': filtered}
    return geo


def list_country_names(map_name='world', include_overseas=False):
    """Return official region/country names available for the given map.

    Parameters
    ----------
    map_name : str, optional
        Map identifier, e.g. ``'world'``, ``'netherlands'``, ``'usa'``.
    include_overseas : bool, optional
        If False, names follow the main-landmass filter (same as the plot).

    Returns
    -------
    list of str
        Sorted feature names from the map geometry.
    """
    geo = load_geojson(map_name, include_overseas=include_overseas)
    names = sorted({
        feat.get('properties', {}).get('name')
        for feat in geo.get('features', [])
        if feat.get('properties', {}).get('name')
    })
    return names


def match_country_names(names, map_name='world', cutoff=0.8, include_overseas=False, logger=None):
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
    official = list_country_names(map_name=map_name, include_overseas=include_overseas)
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

        # 1) alias table (world-level aliases only; e.g. USA, Holland→Netherlands)
        if normalize_map_name(map_name) == 'world' and low in _COUNTRY_ALIASES:
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
                         include_overseas=False,
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
    matched, report = match_country_names(country_names, map_name=map_name, include_overseas=include_overseas, logger=logger)

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
    config['include_overseas'] = kwargs.get('include_overseas', False)
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
            include_overseas=kwargs.get('include_overseas', False),
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

    # Set logo
    config['logo_base64'] = set_logo(filepath=config['logo'])

    return write_html(json_countries, json_data, config, logger)


def build_world_drill_index(logger=None):
    """Map world-country display names → regional map_name keys for drill-down.

    Uses exact / alias matches only (no fuzzy) to avoid false links
    (e.g. England → Greenland).
    """
    ensure_geo_data(logger=logger)
    known_lower = {n.lower(): n for n in _discover_map_names()}
    drill = {}
    try:
        world = load_geojson('world', include_overseas=True, logger=logger)
    except Exception:
        return drill

    def resolve(label):
        low = str(label).strip().lower()
        if low in _MAP_NAME_ALIASES:
            target = _MAP_NAME_ALIASES[low]
            if target != 'world' and target in known_lower:
                return known_lower[target]
            if target in known_lower:
                return known_lower[target]
        if low in known_lower:
            return known_lower[low]
        # file-stem style
        stem = low.replace(' ', '_')
        for k, v in known_lower.items():
            if k.replace(' ', '_') == stem:
                return v
        return None

    for feat in world.get('features') or []:
        name = (feat.get('properties') or {}).get('name')
        if not name:
            continue
        key = resolve(name)
        if key and key != 'world':
            drill[name] = key
    return drill


def _prepare_geo_js_for_html(filepath, logger=None):
    """Expose regional maps next to the HTML for file:// drill-down.

    Browsers block ``fetch()`` of local files from ``file://`` pages (CORS).
    Loading via ``<script src="geo/country.js">`` works. This function:

    1. Reads geometries from ``_geo_dir()`` (package cache).
    2. Writes ``window.__D3BLOCKS_GEO__ = <FeatureCollection>;`` JS wrappers
       into ``<html_dir>/geo/<map>.js`` (once; skipped when already present).

    Returns the relative base ``'geo/'`` for the HTML page.
    """
    ensure_geo_data(logger=logger)
    src_dir = os.path.abspath(_geo_dir())
    if not os.path.isdir(src_dir):
        return 'geo/'

    if filepath:
        html_dir = os.path.dirname(os.path.abspath(str(filepath)))
    else:
        html_dir = os.getcwd()
    if not html_dir:
        html_dir = os.getcwd()

    dest_dir = os.path.join(html_dir, 'geo')
    os.makedirs(dest_dir, exist_ok=True)

    written = 0
    skipped = 0
    for fn in os.listdir(src_dir):
        if not fn.endswith('.geojson'):
            continue
        stem = fn[:-8]  # strip .geojson
        js_name = stem + '.js'
        dest_js = os.path.join(dest_dir, js_name)
        src_geo = os.path.join(src_dir, fn)
        # Skip if JS exists and is newer or same size-ish
        if os.path.isfile(dest_js) and os.path.getmtime(dest_js) >= os.path.getmtime(src_geo):
            skipped += 1
            continue
        try:
            with open(src_geo, 'r', encoding='utf-8') as f:
                payload = f.read()
            with open(dest_js, 'w', encoding='utf-8') as f:
                f.write('window.__D3BLOCKS_GEO__=')
                f.write(payload)
                f.write(';\n')
            written += 1
        except Exception as e:
            if logger is not None:
                logger.warning('Could not write %s: %s' % (dest_js, e))

    if logger is not None:
        logger.info(
            'Geo JS for drill-down: %s (wrote %d, skipped %d; source %s)'
            % (dest_dir, written, skipped, src_dir)
        )
    elif written:
        print('[maps] Prepared %d regional map scripts in %s' % (written, dest_dir))

    return 'geo/'


def write_html(json_countries, json_data, config, logger=None):
    """Write html."""
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])
    width = 'window.screen.width' if config['figsize'][0] is None else config['figsize'][0]
    height = 'window.screen.height' if config['figsize'][1] is None else config['figsize'][1]

    map_name = config.get('map_name', 'world')
    include_overseas = bool(config.get('include_overseas', False))
    try:
        # Always embed full geometry; the UI checkbox filters overseas client-side.
        geo = load_geojson(map_name, include_overseas=True, logger=logger)
        geojson_str = json.dumps(geo, separators=(',', ':'))
        # Always embed world so Back can restore without another fetch
        if normalize_map_name(map_name) == 'world':
            world_geojson_str = geojson_str
        else:
            world_geo = load_geojson('world', include_overseas=True, logger=logger)
            world_geojson_str = json.dumps(world_geo, separators=(',', ':'))
        drill_index = build_world_drill_index(logger=logger)
    except Exception as e:
        if logger is not None:
            logger.error('Failed to load map geometry for %r: %s' % (map_name, e))
        raise

    filepath = config.get('filepath', None)
    geo_fetch_base = _prepare_geo_js_for_html(filepath, logger=logger)

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
        'GEOJSON': geojson_str,
        'WORLD_GEOJSON': world_geojson_str,
        'MAP_NAME': normalize_map_name(map_name),
        'include_overseas': include_overseas,
        'DRILL_INDEX': json.dumps(drill_index, separators=(',', ':')),
        # Relative geo/ next to HTML; JS wrappers built from _geo_dir()
        'GEO_FETCH_BASE': geo_fetch_base,
        'LOGO_BASE64': config['logo_base64'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except Exception:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.maps', package_path='d3js'))

    index_template = jinja_env.get_template('maps.html.j2')
    html = index_template.render(content)
    write_html_file(config, html, logger)
    return html
