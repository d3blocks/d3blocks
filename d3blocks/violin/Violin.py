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
    from .. utils import convert_dataframe_dict, set_path, update_config, write_html_file
except:
    from utils import convert_dataframe_dict, set_path, update_config, write_html_file


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
    """Set the node properties."""
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
        fontsize = fontsize.astype(int)
    # Set size to a minimum of 1
    if isinstance(size, (list, np.ndarray)):
        size = np.array(size)
        size[np.isnan(size)] = 0
        size = np.maximum(size, 0)

    # Convert to dataframe
    df = pd.DataFrame({'x': x, 'y': y, 'color': color, 'size': size, 'stroke': stroke, 'opacity': opacity, 'tooltip': tooltip, 'fontsize': fontsize})

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
    if config['figsize'][0] is None:
        config['figsize'][0] = len(labels) * 95
    if config['figsize'][1] is None:
        config['figsize'][1] = 400

    # Check whether tooltip is available. Otherwise remove the tooltip box.
    if np.all(df['tooltip']=='') or np.all(df['tooltip'].isna()):
        config['mouseover'] = ''
        config['mousemove'] = ''
        config['mouseleave'] = ''
    else:
        config['mouseover'] = '.on("mouseover", mouseover)'
        config['mousemove'] = '.on("mousemove", mousemove)'
        config['mouseleave'] = '.on("mouseleave", mouseleave)'

    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df)
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
        'WIDTH_FIG': config['figsize'][0],
        'HEIGHT_FIG': config['figsize'][1],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
        'SUPPORT': config['support'],
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
    df['y']=df['y'].astype(str)
    # Set x, y
    X = df[['x', 'y', 'color', 'size', 'stroke', 'opacity', 'tooltip', 'fontsize']].to_json(orient='records')
    # Return
    return X
