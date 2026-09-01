"""Violin block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
Licensed    : GPL3
"""

import colourmap
import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
try:
    from .. utils import convert_dataframe_dict, set_path, update_config, write_html_file, include_save_to_svg_script
except:
    from utils import convert_dataframe_dict, set_path, update_config, write_html_file, include_save_to_svg_script


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration settings."""
    logger = kwargs.get('logger', None)
    config['chart'] ='violin'
    config['title'] = kwargs.get('title', 'Violin - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'violin.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['fontsize'] = kwargs.get('fontsize', 12)
    config['bins'] = kwargs.get('bins', 20)
    config['cmap'] = kwargs.get('cmap', 'inferno')
    config['ylim'] = kwargs.get('ylim', [None, None])
    config['x_order'] = kwargs.get('x_order', None)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['fontsize_axis'] = '"' + str(kwargs.get('fontsize_axis', 12)) + 'px"'
    config['fontsize_axis_num'] = kwargs.get('fontsize_axis', 12)
    config['jitter'] = kwargs.get('jitter', 40)
    config['save_button'] = kwargs.get('save_button', True)
    config['show_controls'] = kwargs.get('show_controls', True)
    config['dark_mode'] = kwargs.get('dark_mode', True)
    config['node_text_inside'] = kwargs.get('node_text_inside', True)
    # Return
    return config


# %% Get unique labels
def set_labels(labels, logger=None):
    """Set unique labels."""
    if isinstance(labels, pd.DataFrame) and np.isin(['x'], labels.columns.values):
        if logger is not None: logger.info('Collecting labels from DataFrame using the "x" columns.')
        labels = labels['x'].values.flatten()

    # Checks
    if (labels is None) or len(labels)<1:
        raise Exception(logger.error('Could not extract the labels!'))

    # Get unique categories without sort
    indexes = np.unique(labels, return_index=True)[1]
    uilabels = [labels[index] for index in sorted(indexes)]
    # Return
    return uilabels


def set_node_properties(*args, **kwargs):
    """Set per-point properties for the Violin (same workflow as scatter).

    Accepts one of:
      * None -> returns None
      * pandas.DataFrame with rows matching datapoints; columns become properties
      * dict of column -> array-like (length matches datapoints)
      * list of dicts where each dict is per-point properties

    Returns
    -------
    dict_properties : dict
        Mapping from integer index to property dict for that datapoint.
    """
    logger = kwargs.get('logger', None)
    properties = None
    if len(args) >= 1:
        properties = args[0]
    else:
        properties = kwargs.get('properties', None)

    if properties is None:
        return None

    if isinstance(properties, pd.DataFrame):
        df = properties.reset_index(drop=True)
        dict_props = {}
        for i in range(len(df)):
            row = df.iloc[i].to_dict()
            for k, v in list(row.items()):
                if pd.isna(v):
                    row[k] = None
            dict_props[i] = row
        return dict_props

    if isinstance(properties, dict):
        first = next(iter(properties.values()))
        length = len(first)
        dict_props = {}
        for i in range(length):
            p = {}
            for k, v in properties.items():
                try:
                    val = v[i]
                except Exception:
                    val = None
                p[k] = None if (val is None or (isinstance(val, float) and np.isnan(val))) else val
            dict_props[i] = p
        return dict_props

    if isinstance(properties, (list, tuple)):
        dict_props = {}
        for i, it in enumerate(properties):
            if isinstance(it, dict):
                dict_props[i] = it
            else:
                dict_props[i] = {'value': it}
        return dict_props

    if logger is not None:
        logger.info('Could not parse properties for violin; ignoring.')
    return None


def set_edge_properties(*args, **kwargs):
    """Set the properties for the Violin block.

    Parameters
    ----------
    x : list of String or numpy array.
        This 1d-vector contains the class labels for each datapoint in y.
    y : list of float or numpy array.
        This 1d-vector contains the values for the samples.
    size: list/array of with same size as (x,y). Can be of type str or int.
        Size of the samples.
    color: list/array of hex colors with same size as y
        '#002147' : All dots/nodes are get the same hex color.
        None: The colors are generated on value using the colormap specified in cmap.
        ['#000000', '#ffffff',...]: list/array of hex colors with same size as y.
    x_order : list of String (default: None)
        The order of the class labels on the x-axis.
        ["setosa", "versicolor", "virginica"]
    opacity: float or list/array [0-1] (default: 0.6)
        Opacity of the dot. Shoud be same size as (x,y)
    stroke: list/array of hex colors with same size as (x,y)
        Edgecolor of dot in hex colors.
        '#000000' : Edge colors are all black.
    tooltip: list of labels with same size as (x,y)
        labels of the samples.
    cmap : String, (default: 'inferno')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
    fontsize : int, optional (default: 12)
        Text fontsize.
    properties : dict, list of dicts, or pd.DataFrame, (default: None)
        User-defined properties for each datapoint (same workflow as scatter).
        Every column becomes a property offered in the Layout panel to drive
        size (numeric), color (numeric or categorical), shape (categorical),
        or label.
            * None: No additional properties.
            * {'age': [22, 41], 'labx': ['A', 'B']}: dict of array-like, same length as (x, y).
            * pd.DataFrame with same number of rows as (x, y).

    Returns
    -------
    d3.edge_properties: DataFrame of dictionary
         Contains properties of the unique input edges/links.
    """
    # Collect arguments
    if len(args)==2:
        x, y = args
    else:
        x = kwargs.get('x', None)
        y = kwargs.get('y', None)
    # Collect key-word arguments
    color = kwargs.get('color', None)
    size = kwargs.get('size', 5)
    stroke = kwargs.get('stroke', '#ffffff')
    opacity = kwargs.get('opacity', 0.8)
    tooltip = kwargs.get('tooltip', '')
    cmap = kwargs.get('cmap', 'inferno')
    fontsize = kwargs.get('fontsize', 12)
    x_order = kwargs.get('x_order', None)
    properties = kwargs.get('properties', None)
    logger = kwargs.get('logger', None)

    # Make checks
    if len(x)!=len(y): raise Exception(logger.error('input parameter "x" should be of size of "y".'))
    if size is None: raise Exception(logger.error('input parameter "size" should have value >0.'))
    if stroke is None: raise Exception(logger.error('input parameter "stroke" should have hex value.'))
    if opacity is None: raise Exception(logger.error('input parameter "opacity" should have value in range [0..1].'))

    if isinstance(stroke, (list, np.ndarray)) and (len(stroke)!=len(x)): raise Exception(logger.error('input parameter "stroke" should be of same size of (x, y).'))
    if isinstance(size, (list, np.ndarray)) and (len(size)!=len(x)): raise Exception(logger.error('input parameter "s" should be of same size of (x, y).'))
    if isinstance(opacity, (list, np.ndarray)) and (len(opacity)!=len(x)): raise Exception(logger.error('input parameter "opacity" should be of same size of (x, y).'))
    if isinstance(fontsize, (list, np.ndarray)) and (len(fontsize)!=len(x)): raise Exception(logger.error('input parameter "fontsize" should be of same size of (x, y).'))

    # Set fontsize to a minimum of 0
    if isinstance(fontsize, (list, np.ndarray)):
        fontsize=np.array(fontsize)
        fontsize[np.isnan(fontsize)] = 0
        fontsize = np.maximum(fontsize, 0)
        # Convert NumPy integers to regular Python integers for proper JSON serialization
        fontsize = [int(x) for x in fontsize]
    # Set size to a minimum of 1
    if isinstance(size, (list, np.ndarray)):
        size = np.array(size)
        size[np.isnan(size)] = 0
        size = np.maximum(size, 0)

    # Convert to dataframe
    df = pd.DataFrame({'x': x, 'y': y, 'color': color, 'size': size, 'stroke': stroke, 'opacity': opacity, 'tooltip': tooltip, 'fontsize': fontsize})

    # Attach per-point properties (aligned with x/y before filtering so masks stay in sync).
    # Accept either:
    #   - index -> dict (output of set_node_properties(df))  ← scatter workflow
    #   - column-oriented dict / DataFrame / list of dicts
    n = len(df)
    props_col = [None] * n
    if properties is not None:
        props_map = None
        if isinstance(properties, dict) and len(properties) > 0:
            first_val = next(iter(properties.values()))
            # Already index -> property-dict (from set_node_properties)
            if isinstance(first_val, dict):
                props_map = properties
        if props_map is None:
            props_map = set_node_properties(properties, logger=logger)
        if props_map is not None:
            for i in range(n):
                props_col[i] = props_map.get(i) or props_map.get(str(i))
    df['_properties'] = props_col

    # Remove NaN values
    Irem = df['y'].isna()
    if np.any(Irem):
        if logger is not None: logger.info('Removing [%.0d] NaN values.' %(sum(Irem)))
        df = df.loc[~Irem, :]

    # Filter on class labels
    if x_order is not None:
        classes = "|".join(x_order)
        df = df.loc[df['x'].str.contains(classes), :]
        if logger is not None: logger.info('Filter on: [%s]' %(classes))

    # Color on values and cmap (after cleaning and filtering)
    if color is None:
        df['color'] = colourmap.fromlist(df['y'].values, scheme='hex', cmap=cmap)[0]

    df.reset_index(inplace=True, drop=True)
    if logger is not None: logger.info('Number of samples: %d' %(df.shape[0]))
    return df


def show(df, **kwargs):
    """Show the Violin chart.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    bins : Int (default: 50)
        The bin size is the 'resolution' of the violin plot.
    ylim : tuple, (default: [None, None])
        Limit the width of the y-axis [min, max].
        [None, None] : The width is determined based on the min-max value range.
    title : String, (default: None)
        Title of the figure.
    filepath : String, (Default: user temp directory)
        File path to save the output.
        'c://temp//Violin.html'
    figsize : tuple, (default: [None, None])
        Size of the figure in the browser, [width, height].
        [None, None]: The width is auto-determined based on the #labels.
    showfig : bool, (default: True)
        True: Open browser-window.
        False: Do not open browser-window.
    overwrite : bool, (default: True)
        True: Overwrite the html in the destination directory.
        False: Do not overwrite destination file but show warning instead.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    df = convert_dataframe_dict(df, frame=True)
    labels = np.unique(df['x'].values)

    spacing = 0.10
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        y_spacing = (df['y'].max() - df['y'].min()) * spacing
        config['ylim'] = [df['y'].min() - y_spacing, df['y'].max() + y_spacing]
    # Ordering the class labels
    if config['x_order'] is None:
        config['x_order'] = str(list(labels))
    # None width → fit browser width client-side
    # None height → 70% of browser window height client-side
    # Numeric fallbacks are only used before JS measures the viewport.
    config['auto_width'] = config['figsize'][0] is None
    config['auto_height'] = config['figsize'][1] is None
    if config['figsize'][0] is None:
        config['figsize'][0] = max(int(len(labels) * 95), 800)
    if config['figsize'][1] is None:
        config['figsize'][1] = 600  # fallback ≈ 70% of a typical 900px-tall window

    # Check whether tooltip is available. Otherwise remove the tooltip box.
    if np.all(df['tooltip']=='') or np.all(df['tooltip'].isna()):
        config['mouseover'] = ''
        config['mousemove'] = ''
        config['mouseleave'] = ''
    else:
        config['mouseover'] = '.on("mouseover", mouseover)'
        config['mousemove'] = '.on("mousemove", mousemove)'
        config['mouseleave'] = '.on("mouseleave", mouseleave)'

    # Create the data from the input of javascript (include df/node properties for Layout)
    node_properties = kwargs.get('node_properties', None)
    X, prop_keys = get_data_ready_for_d3(df, node_properties=node_properties)
    config['property_keys'] = prop_keys
    # Write to HTML
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : list of str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    None.

    """
    # Save button
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])
    # Ensure new GUI keys have defaults (backwards compatible)
    show_controls = config.get('show_controls', True)
    dark_mode = config.get('dark_mode', True)
    jitter = config.get('jitter', 40)
    fontsize_axis_num = config.get('fontsize_axis_num', 12)
    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'MIN_Y': config['ylim'][0],
        'MAX_Y': config['ylim'][1],
        'X_ORDER': config['x_order'],
        'BINS': config['bins'],
        'FONTSIZE_AXIS': config['fontsize_axis'],
        'FONTSIZE_AXIS_NUM': fontsize_axis_num,
        'JITTER': jitter,
        'WIDTH_FIG': config['figsize'][0],
        'HEIGHT_FIG': config['figsize'][1],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
        'SUPPORT': config['support'],
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
        'showControls': 'true' if show_controls else 'false',
        'darkMode': 'true' if dark_mode else 'false',
        'PROPERTY_KEYS_JSON': __import__('json').dumps(config.get('property_keys', [])),
        'NODE_TEXT_INSIDE': 'true' if config.get('node_text_inside', True) else 'false',
        'AUTO_WIDTH': 'true' if config.get('auto_width', False) else 'false',
        'AUTO_HEIGHT': 'true' if config.get('auto_height', False) else 'false',
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.violin', package_path='d3js'))

    index_template = jinja_env.get_template('violin.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


def get_data_ready_for_d3(df, node_properties=None):
    """Convert the source-target data into d3 compatible data.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data (edge_properties).
    node_properties : dict, optional
        Index -> property dict. Used when properties were not already
        stored on df as '_properties' (scatter-compatible path).

    Returns
    -------
    X : str.
        JSON list of records. Each record includes a ``properties`` object
        (or null) so the Layout panel can drive size/color/shape/label from
        DataFrame columns.
    """
    out = df.copy()
    out['y'] = out['y'].astype(str)

    def _has_props(series):
        if series is None:
            return False
        for v in series:
            if isinstance(v, dict) and len(v) > 0:
                return True
        return False

    if '_properties' not in out.columns or not _has_props(out['_properties']):
        if node_properties is not None:
            # Accept DataFrame, index->dict, or column-oriented inputs
            if isinstance(node_properties, pd.DataFrame):
                props_map = set_node_properties(node_properties)
            elif isinstance(node_properties, dict) and len(node_properties) > 0:
                first_val = next(iter(node_properties.values()))
                if isinstance(first_val, dict):
                    props_map = node_properties  # index -> prop dict
                else:
                    props_map = set_node_properties(node_properties)
            else:
                props_map = set_node_properties(node_properties)
            if props_map is not None:
                out['_properties'] = [
                    props_map.get(i) or props_map.get(str(i))
                    for i in range(len(out))
                ]
            else:
                out['_properties'] = [None] * len(out)
        elif '_properties' not in out.columns:
            out['_properties'] = [None] * len(out)

    def _json_safe(v):
        if v is None:
            return None
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            if np.isnan(v):
                return None
            return float(v)
        if isinstance(v, float) and np.isnan(v):
            return None
        if isinstance(v, (np.bool_,)):
            return bool(v)
        return v

    records = []
    prop_keys = set()
    cols = ['x', 'y', 'color', 'size', 'stroke', 'opacity', 'tooltip', 'fontsize']
    for i in range(len(out)):
        row = {c: _json_safe(out.iloc[i][c]) for c in cols}
        prop = out.iloc[i]['_properties'] if '_properties' in out.columns else None
        if prop is not None and isinstance(prop, dict):
            clean = {k: _json_safe(v) for k, v in prop.items()}
            row['properties'] = clean
            prop_keys.update(clean.keys())
        else:
            row['properties'] = None
        records.append(row)

    import json
    return json.dumps(records), sorted(prop_keys)
