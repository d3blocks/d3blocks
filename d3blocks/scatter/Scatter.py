"""Scatter block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

# import colourmap

import numpy as np
import pandas as pd
import json
from jinja2 import Environment, PackageLoader
from pathlib import Path

try:
    from .. utils import set_colors, convert_dataframe_dict, set_path, update_config, write_html_file, jitter_func, include_save_to_svg_script
except:
    from utils import set_colors, convert_dataframe_dict, set_path, update_config, write_html_file, jitter_func, include_save_to_svg_script


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Scatter'
    config['title'] = kwargs.get('title', 'scatter - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'scatter.html'), logger)
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['figsize'] = kwargs.get('figsize', [1150, 768])
    config['cmap'] = kwargs.get('cmap', 'tab20')
    config['scale'] = kwargs.get('scale', False)
    config['ylim'] = kwargs.get('ylim', [None, None])
    config['xlim'] = kwargs.get('xlim', [None, None])
    config['label_radio'] = kwargs.get('label_radio', ['(x, y)', '(x1, y1)', '(x2, y2)', '(x3, y3)'])
    config['color_background'] = kwargs.get('color_background', '#ffffff')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['jitter'] = kwargs.get('jitter', None)
    config['save_button'] = kwargs.get('save_button', True)
    # Return
    return config


# %% Preprocessing
def check_exceptions(x, y, x1, y1, x2, y2, x3, y3, size, color, tooltip, logger):
    """Check Exceptions."""
    # if len(config['label_radio'])!=sum(list(map(lambda x: x=='', config['radio_button_visible']))): raise Exception(logger.error('input parameter [label_radio] must contain the correct number of labels depending on the (x,y), (x1,y1), (x2,y2), (x3,y3) coordinates.'))
    if len(x)!=len(y): raise Exception(logger.error('input parameter [x] and [y] should be of size of (x, y).'))
    if size is None: raise Exception(logger.error('input parameter [size] should have value >0.'))
    if color is None: raise Exception(logger.error('input parameter [color] should be of a list of string with hex color, such as "#000000".'))
    if isinstance(size, (list, np.ndarray)) and (len(size)!=len(x)): raise Exception(logger.error('input parameter [s] should be of same size of (x, y).'))
    if (tooltip is not None) and len(tooltip)!=len(x): raise Exception(logger.error('input parameter [tooltip] should be of size (x, y) and not None.'))

    if (x1 is not None) or (y1 is not None):
        if len(x1)!=len(y1): raise Exception(logger.error('input parameter [x1] should be of size of (x1, y1).'))
        if len(x)!=len(x1): raise Exception(logger.error('input parameter (x1, y1) should be of size of (x, y).'))
    if (x2 is not None) or (y2 is not None):
        if len(x2)!=len(y2): raise Exception(logger.error('input parameter [x2] should be of size of (x2, y2).'))
        if len(x)!=len(x2): raise Exception(logger.error('input parameter (x2, y2) should be of size of (x, y).'))
    if (x3 is not None) or (y3 is not None):
        if len(x3)!=len(y3): raise Exception(logger.error('input parameter [x3] should be of size of (x3, y3).'))
        if len(x)!=len(x3): raise Exception(logger.error('input parameter (x3, y3) should be of size of (x, y).'))


# %% Set the Node properties
def set_node_properties(*args, **kwargs):
    """Set the node properties for scatter.

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
    import pandas as pd
    logger = kwargs.get('logger', None)
    properties = None
    # Allow positional first arg
    if len(args)>=1:
        properties = args[0]
    else:
        properties = kwargs.get('properties', None)

    if properties is None:
        return None

    # DataFrame -> dict of rows
    if isinstance(properties, pd.DataFrame):
        df = properties.reset_index(drop=True)
        dict_props = {}
        for i in range(len(df)):
            # convert NaNs to None
            row = df.iloc[i].to_dict()
            for k, v in list(row.items()):
                if pd.isna(v):
                    row[k] = None
            dict_props[i] = row
        return dict_props

    # dict of columns -> array-like
    if isinstance(properties, dict):
        # keys are property names; values are list-like
        # determine length
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
                p[k] = None if (val is None) else val
            dict_props[i] = p
        return dict_props

    # list of dicts
    if isinstance(properties, (list, tuple)):
        dict_props = {}
        for i, it in enumerate(properties):
            if isinstance(it, dict):
                dict_props[i] = it
            else:
                dict_props[i] = {'value': it}
        return dict_props

    # Fallback
    if logger is not None:
        logger.info('Could not parse properties for scatter; ignoring.')
    return None


# %% Set the edge properties
def set_edge_properties(*args, **kwargs):
    """Set the edge properties for the scatterplot block.

    Parameters
    ----------
    x : numpy array
        1d coordinates x-axis.
    y : numpy array
        1d coordinates y-axis.
    x1 : numpy array
        Second set of 1d coordinates x-axis.
    y1 : numpy array
        Second set of 1d coordinates y-axis.
    x2 : numpy array
        Third set of 1d coordinates x-axis.
    y2 : numpy array
        Third set of 1d coordinates y-axis.
    x3 : numpy array
        Fourth set of 1d coordinates x-axis.
    y3 : numpy array
        Fourth set of 1d coordinates y-axis.
    size: list/array of with same size as (x,y). Can be of type str or int.
        Size of the samples.
    color: list/array of hex colors with same size as (x,y)
        '#ffffff' : All dots are get the same hex color.
        None: The same color as for c is applied.
        ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
    stroke: list/array of hex colors with same size as (x,y)
        Edgecolor of dotsize in hex colors.
        '#000000' : All dots are get the same hex color.
        ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
    c_gradient : String, (default: None)
        Make a lineair gradient based on the density for the particular class label.
        '#ffffff'
    tooltip: list of labels with same size as (x,y)
        labels of the samples.
    opacity: float or list/array [0-1]
        Opacity of the dot. Shoud be same size as (x,y)
    cmap : String, (default: 'inferno')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
    scale: Bool, optional
        Scale datapoints. The default is False.
    properties: dict, list of dicts, or pd.DataFrame, (default: None)
        User-defined properties for each datapoint, with the same logic as node_properties in d3graph.
        Every column becomes a property that is: (1) shown in the bottom menu when a point is clicked,
        and (2) offered as an interactive control to drive the point size (continuous/numeric columns)
        or point shape (categorical/string columns).
            * None: No additional properties are stored.
            * {'age': [22, 41, 35], 'category': ['A', 'B', 'A']}: dict of array-like, same length as (x, y).
            * pd.DataFrame with same number of rows as (x, y). Column names become the property names.

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
    x1 = kwargs.get('x1', None)
    y1 = kwargs.get('y1', None)
    x2 = kwargs.get('x2', None)
    y2 = kwargs.get('y2', None)
    x3 = kwargs.get('x3', None)
    y3 = kwargs.get('y3', None)

    jitter = kwargs.get('jitter', None)
    size = kwargs.get('size', 5)
    color = kwargs.get('color', '#69b3a2')
    stroke = kwargs.get('stroke', '#000000')
    c_gradient = kwargs.get('c_gradient', None)
    tooltip = kwargs.get('tooltip', None)
    opacity = kwargs.get('opacity', 0.8)
    cmap = kwargs.get('cmap', 'tab20')
    scale = kwargs.get('scale', False)
    logger = kwargs.get('logger', None)

    if isinstance(size, list): size=np.array(size)

    if (x1 is None): x1 = np.zeros_like(x) * np.nan
    if (y1 is None): y1 = np.zeros_like(x) * np.nan
    if (x2 is None): x2 = np.zeros_like(x) * np.nan
    if (y2 is None): y2 = np.zeros_like(x) * np.nan
    if (x3 is None): x3 = np.zeros_like(x) * np.nan
    if (y3 is None): y3 = np.zeros_like(x) * np.nan

    # Add jitter
    x = jitter_func(x, jitter=jitter)
    y = jitter_func(y, jitter=jitter)
    x1 = jitter_func(x1, jitter=jitter)
    y1 = jitter_func(y1, jitter=jitter)
    x2 = jitter_func(x2, jitter=jitter)
    y2 = jitter_func(y2, jitter=jitter)
    x3 = jitter_func(x3, jitter=jitter)
    y3 = jitter_func(y3, jitter=jitter)

    # Combine into array
    X = np.c_[x, y]
    # Combine second coordinates into array
    X1 = np.c_[x1, y1]
    X2 = np.c_[x2, y2]
    X3 = np.c_[x3, y3]

    # Scale data
    if scale:
        if logger is not None: logger.info('Scaling xy-coordinates.')
        X = _scale_xy(X)
        X1 = _scale_xy(X1)
        X2 = _scale_xy(X2)
        X3 = _scale_xy(X3)

    # In case only one (s)ize is defined. Set all points to this size.
    if isinstance(size, (int, float)): size = np.repeat(size, X.shape[0])
    if np.any(size<0):
        if logger is not None: logger.info('[%.0d] sizes are <0 and set to 0.' %(np.sum(size<0)))
        size[size<0]=0

    # In case None tooltip is defined. Set all points to this tooltip.
    if tooltip is None: tooltip = np.repeat('', X.shape[0])

    # Set colors
    color, labels = set_colors(X, color, cmap, c_gradient=c_gradient)

    # In case only one opacity is defined. Set all points to this size.
    if isinstance(opacity, (int, float)): opacity = np.repeat(opacity, X.shape[0])
    if (c_gradient is not None):
        if logger is not None: logger.info('Set opacity based on the data density.')
        import colourmap
        c_rgb = colourmap.gradient_on_density_color(X, colourmap.hex2rgb(color), labels, opaque_type='per_class')
        opacity = c_rgb[:, 3]
        # c_hex = c_rgb[:, 0:3]

    # In case stroke is None: use same colors as for c.
    if stroke is None:
        stroke = color
    elif isinstance(stroke, str):
        # In case only one stroke is defined. Set all points to this size.
        stroke = np.repeat(stroke, X.shape[0])

    # Make dict with properties
    dict_properties = {}
    for i in range(0, X.shape[0]):
        dict_properties[i] = {'label': labels[i], 'x': X[i][0], 'y': X[i][1], 'x1': X1[i][0], 'y1': X1[i][1], 'x2': X2[i][0], 'y2': X2[i][1], 'x3': X3[i][0], 'y3': X3[i][1], 'color': color[i], 'size': size[i], 'stroke': stroke[i], 'opacity': opacity[i], 'tooltip': tooltip[i]}

    # return
    return dict_properties


# %% Scale data
def _scale_xy(X):
    """Scale xy coordinates."""
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    return (X - x_min) / (x_max - x_min)


# %% Show
def show(df, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    label_radio: List ['(x, y)', '(x1, y1)', '(x2, y2)', '(x3, y3)']
        The labels used for the radiobuttons.
    set_xlim : tuple, (default: [None, None])
        Width of the x-axis: The default is extracted from the data with 10% spacing.
    set_ylim : tuple, (default: [None, None])
        Height of the y-axis: The default is extracted from the data with 10% spacing.
    title : String, (default: None)
        Title of the figure.
        'Scatterplot'
    filepath : String, (Default: user temp directory)
        File path to save the output.
        'c://temp//Scatter_demo.html'
    figsize : tuple, (default: [None, None])
        Size of the figure in the browser, [width, height].
        [900, 600]
    showfig : bool, (default: True)
        True: Open browser-window.
        False: Do not open browser-window.
    overwrite : bool, (default: True)
        True: Overwrite the html in the destination directory.
        False: Do not overwrite destination file but show warning instead.
    reset_properties : bool, (default: True)
        True: Reset the node_properties at each run.
        False: Use the d3.node_properties()
    config : dict
        Dictionary containing configuration keys.
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    df = df.copy()
    logger = kwargs.get('logger', None)
    label_radio = kwargs.get('label_radio', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    if label_radio is not None:
        config['label_radio'] = label_radio

    # Convert dict/frame.
    df = convert_dataframe_dict(df, frame=True)

    # Set the radio button and visibility of the labels
    config['radio_button_visible'] = ["",
                                      ("display:none;" if (np.all(list(map(np.isnan, df['x1'])))) else ""),
                                      ("display:none;" if (np.all(list(map(np.isnan, df['x2'])))) else ""),
                                      ("display:none;" if (np.all(list(map(np.isnan, df['x3'])))) else "")]
    # Ensure label_radio has length 4
    while len(config['label_radio']) < 4:
        config['label_radio'].append("")
    if ("display:none" in config['radio_button_visible'][1]): config['label_radio'][1]=""
    if ("display:none" in config['radio_button_visible'][2]): config['label_radio'][2]=""
    if ("display:none" in config['radio_button_visible'][3]): config['label_radio'][3]=""

    # Compute xlim and ylim for the axis.
    spacing = 0.12
    if config['xlim']==[None, None] or len(config['xlim'])==0:
        maxvalue = df[['x', 'x1', 'x2', 'x3']].max().max()
        minvalue = df[['x', 'x1', 'x2', 'x3']].min().min()
        x_spacing = ((maxvalue - minvalue) * spacing)
        config['xlim'] = [minvalue - x_spacing, maxvalue + x_spacing]
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        maxvalue = df[['y', 'y1', 'y2', 'y3']].max().max()
        minvalue = df[['y', 'y1', 'y2', 'y3']].min().min()
        y_spacing = ((maxvalue - minvalue) * spacing)
        config['ylim'] = [minvalue - y_spacing, maxvalue + y_spacing]

    # Get node_properties from kwargs (passed by D3Blocks.show)
    node_properties = kwargs.get('node_properties', None)
    # Create the data from the input for javascript, include node_properties when provided
    X = get_data_ready_for_d3(df, node_properties=node_properties)
    
    # Check whether tooltip is available. Otherwise remove the tooltip box.
    if np.all(df['tooltip']==''):
        config['mouseover'] = ''
        config['mousemove'] = ''
        config['mouseleave'] = ''
    else:
        config['mouseover'] = '.on("mouseover", mouseover)'
        config['mousemove'] = '.on("mousemove", mousemove)'
        config['mouseleave'] = '.on("mouseleave", mouseleave)'

    # Write to HTML
    return write_html(X, config, logger=logger)


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
    content = {
        'json_data': X,
        'COLOR_BACKGROUND': config['color_background'],
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'MIN_X': config['xlim'][0],
        'MAX_X': config['xlim'][1],
        'MIN_Y': config['ylim'][0],
        'MAX_Y': config['ylim'][1],
        'RADIO_LABEL1': config['label_radio'][0],
        'RADIO_LABEL2': config['label_radio'][1],
        'RADIO_LABEL3': config['label_radio'][2],
        'RADIO_LABEL4': config['label_radio'][3],
        'RADIO_VISIBLE1': config['radio_button_visible'][0],
        'RADIO_VISIBLE2': config['radio_button_visible'][1],
        'RADIO_VISIBLE3': config['radio_button_visible'][2],
        'RADIO_VISIBLE4': config['radio_button_visible'][3],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
        'SUPPORT': config['support'],
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.scatter', package_path='d3js'))

    index_template = jinja_env.get_template('scatter.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


def get_data_ready_for_d3(df, node_properties=None):
    """Convert the edge_properties dataframe into d3 compatible JSON.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data (edge_properties converted to DataFrame by caller).
    node_properties : dict-like or DataFrame, optional
        Per-point properties. If provided, the properties for each point will be
        appended as the last element of each row's array so client-side code can
        access them as `d[13]`.

    Returns
    -------
    X : str
        JSON string representing list-of-arrays where each array contains:
        [x, y, color, size, opacity, stroke, tooltip, x1, y1, x2, y2, x3, y3, properties|null]
    """
    # Ensure df is a DataFrame
    if not isinstance(df, (list, tuple)):
        # df is expected to be a DataFrame already (convert_dataframe_dict done by caller)
        try:
            # Keep only expected columns and ensure ordering
            cols = ['x', 'y', 'color', 'size', 'opacity', 'stroke', 'tooltip', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3']
            rows = df[cols].values.tolist()
        except Exception:
            # Fallback: try converting whole df to list of lists
            rows = pd.DataFrame(df).values.tolist()
    else:
        rows = list(df)

    # Normalize node_properties into a mapping idx->dict
    props_map = None
    if node_properties is not None:
        try:
            if isinstance(node_properties, pd.DataFrame):
                props_map = {}
                for i in range(len(node_properties)):
                    row = node_properties.iloc[i].to_dict()
                    for k, v in list(row.items()):
                        if pd.isna(v): row[k] = None
                    props_map[i] = row
            elif isinstance(node_properties, dict):
                props_map = node_properties
            elif isinstance(node_properties, (list, tuple)):
                # list of dicts
                props_map = {}
                for i, it in enumerate(node_properties):
                    props_map[i] = it if isinstance(it, dict) else {'value': it}
        except Exception:
            # Last resort, try to treat as dict-like
            try:
                props_map = dict(node_properties)
            except Exception:
                props_map = None
    # Build output array-of-arrays and append property object or null
    out = []
    for i, r in enumerate(rows):
        # ensure r is list
        row = list(r)
        prop = None
        if props_map is not None:
            # props_map might use string keys; try int and str
            if i in props_map:
                prop = props_map[i]
            elif str(i) in props_map:
                prop = props_map[str(i)]
            else:
                # If props_map is a dict of column->list, handle earlier in set_node_properties
                prop = None
        # Append properties as last element
        row.append(prop)
        out.append(row)
    # dump to json
    return json.dumps(out)
