"""Scatter block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

# import colourmap

import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time

try:
    from .. utils import set_colors, convert_dataframe_dict, set_path, update_config, write_html_file, jitter_func
except:
    from utils import set_colors, convert_dataframe_dict, set_path, update_config, write_html_file, jitter_func


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Scatter'
    config['title'] = kwargs.get('title', 'scatter - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'scatter.html'), logger)
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['figsize'] = kwargs.get('figsize', [900, 600])
    config['cmap'] = kwargs.get('cmap', 'tab20')
    config['scale'] = kwargs.get('scale', False)
    config['ylim'] = kwargs.get('ylim', [None, None])
    config['xlim'] = kwargs.get('xlim', [None, None])
    config['label_radio'] = kwargs.get('label_radio', ['(x, y)', '(x1, y1)', '(x2, y2)'])
    config['color_background'] = kwargs.get('color_background', '#ffffff')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['jitter'] = kwargs.get('jitter', None)
    # Return
    return config


# %% Preprocessing
def check_exceptions(x, y, x1, y1, x2, y2, size, color, tooltip, logger):
    """Check Exceptions."""
    # if len(config['label_radio'])!=sum(list(map(lambda x: x=='', config['radio_button_visible']))): raise Exception(logger.error('input parameter [label_radio] must contain the correct number of labels depending on the (x,y), (x1,y1), (x2,y2) coordinates.'))
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


# %% Set the Node properties
def set_node_properties(*args, **kwargs):
    """Set the node properties."""
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

    # if (x1 is None): x1 = x
    # if (y1 is None): y1 = y
    # if (x2 is None): x2 = x
    # if (y2 is None): y2 = y

    if (x1 is None): x1 = np.zeros_like(x) * np.nan
    if (y1 is None): y1 = np.zeros_like(x) * np.nan
    if (x2 is None): x2 = np.zeros_like(x) * np.nan
    if (y2 is None): y2 = np.zeros_like(x) * np.nan

    # Add jitter
    x = jitter_func(x, jitter=jitter)
    y = jitter_func(y, jitter=jitter)
    x1 = jitter_func(x1, jitter=jitter)
    y1 = jitter_func(y1, jitter=jitter)
    x2 = jitter_func(x2, jitter=jitter)
    y2 = jitter_func(y2, jitter=jitter)

    # if jitter is None or jitter is False: jitter=0
    # if jitter is True: jitter=0.01
    # if jitter>0:
    #     if logger is not None: logger.info('Add jitter [%g] to xy-coordinates.' %(jitter))
    #     x = x + np.random.normal(0, jitter, size=len(x))
    #     if y is not None: y = y + np.random.normal(0, jitter, size=len(y))
    #     if x1 is not None: x1 = x1 + np.random.normal(0, jitter, size=len(x1))
    #     if x2 is not None: x2 = x2 + np.random.normal(0, jitter, size=len(x2))
    #     if y1 is not None: y1 = y1 + np.random.normal(0, jitter, size=len(y1))
    #     if y2 is not None: y2 = y2 + np.random.normal(0, jitter, size=len(y2))

    # Combine into array
    X = np.c_[x, y]
    # Combine second coordinates into array
    X1 = np.c_[x1, y1]
    X2 = np.c_[x2, y2]

    # Scale data
    if scale:
        if logger is not None: logger.info('Scaling xy-coordinates.')
        X = _scale_xy(X)
        X1 = _scale_xy(X1)
        X2 = _scale_xy(X2)

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
        dict_properties[i] = {'label': labels[i], 'x': X[i][0], 'y': X[i][1], 'x1': X1[i][0], 'y1': X1[i][1], 'x2': X2[i][0], 'y2': X2[i][1], 'color': color[i], 'size': size[i], 'stroke': stroke[i], 'opacity': opacity[i], 'tooltip': tooltip[i]}

    # Create the plot
    # df = pd.DataFrame(dict_properties).T

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
    label_radio: List ['(x, y)', '(x1, y1)', '(x2, y2)']
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
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    df = convert_dataframe_dict(df, frame=True)

    # Set the radio button and visibility of the labels
    config['radio_button_visible'] = [("display:none;" if (np.all(list(map(np.isnan, df['x1'])))) else ""),
                                      ("display:none;" if (np.all(list(map(np.isnan, df['x1'])))) else ""),
                                      ("display:none;" if (np.all(list(map(np.isnan, df['x2'])))) else "")]
    if ("display:none" in config['radio_button_visible'][0]): config['label_radio'][0]=""
    if ("display:none" in config['radio_button_visible'][1]): config['label_radio'][1]=""
    if len(config['label_radio'])==3 and ("display:none" in config['radio_button_visible'][2]):
        config['label_radio'][2]=""
    elif len(config['label_radio'])==2:
        config['label_radio'].append("")

    # Compute xlim and ylim for the axis.
    spacing = 0.12
    if config['xlim']==[None, None] or len(config['xlim'])==0:
        maxvalue = df[['x', 'x1', 'x2']].max().max()
        minvalue = df[['x', 'x1', 'x2']].min().min()
        x_spacing = ((maxvalue - minvalue) * spacing)
        config['xlim'] = [minvalue - x_spacing, maxvalue + x_spacing]
        # x_spacing = (df['x'].max() - df['x'].min()) * spacing
        # config['xlim'] = [df['x'].min() - x_spacing, df['x'].max() + x_spacing]
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        maxvalue = df[['y', 'y1', 'y2']].max().max()
        minvalue = df[['y', 'y1', 'y2']].min().min()
        y_spacing = ((maxvalue - minvalue) * spacing)
        config['ylim'] = [minvalue - y_spacing, maxvalue + y_spacing]
        # y_spacing = (df['y'].max() - df['y'].min()) * spacing
        # config['ylim'] = [df['y'].min() - y_spacing, df['y'].max() + y_spacing]

    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df)
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
        'RADIO_VISIBLE1': config['radio_button_visible'][0],
        'RADIO_VISIBLE2': config['radio_button_visible'][1],
        'RADIO_VISIBLE3': config['radio_button_visible'][2],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.scatter', package_path='d3js'))

    index_template = jinja_env.get_template('scatter.html.j2')

    # index_file = Path(config['filepath'])
    # # index_file.write_text(index_template.render(content))
    # if config['overwrite'] and os.path.isfile(index_file):
    #     if logger is not None: logger.info('File already exists and will be overwritten: [%s]' %(index_file))
    #     os.remove(index_file)
    #     time.sleep(0.5)
    # with open(index_file, "w", encoding="utf-8") as f:
    #     f.write(index_template.render(content))

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


def get_data_ready_for_d3(df):
    """Convert the source-target data into d3 compatible data.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.

    Returns
    -------
    X : str.
        Converted data into a string that is d3 compatible.

    """
    # Set x, y
    X = df[['x', 'y', 'color', 'size', 'opacity', 'stroke', 'tooltip', 'x1', 'y1', 'x2', 'y2']].to_json(orient='values')
    # Return
    return X
