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
    from .. utils import convert_dataframe_dict, set_path
except:
    from utils import convert_dataframe_dict, set_path


# %% Get unique labels
def set_labels(df):
    return np.unique(df['x'].values)


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration settings."""
    config['chart'] ='violin'
    config['title'] = kwargs.get('title', 'Violin - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'violin.html'))
    config['figsize'] = kwargs.get('figsize', [None, None])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['bins'] = kwargs.get('bins', 20)
    config['cmap'] = kwargs.get('cmap', 'inferno')
    config['ylim'] = kwargs.get('ylim', [None, None])
    config['x_order'] = kwargs.get('x_order', None)
    # Return
    return config


def set_node_properties(labels, cmap, logger, **kwargs):
    """Set the node properties."""
    dict_labels = {}
    for i, label in enumerate(labels):
        dict_labels[label] = {'id': i, 'label': label}
    # Return
    return dict_labels


def set_edge_properties(x, y, config, color=None, size=5, stroke='#ffffff', opacity=0.8, tooltip='', logger=None):
    # Convert to dataframe
    df = pd.DataFrame({'x': x, 'y': y, 'color': color, 'size': size, 'stroke': stroke, 'opacity': opacity, 'tooltip': tooltip})

    # Remove NaN values
    Irem = df['y'].isna()
    if np.any(Irem):
        logger.info('Removing [%.0d] NaN values.' %(sum(Irem)))
        df = df.loc[~Irem, :]

    # Filter on class labels
    if config['x_order'] is not None:
        classes = "|".join(config['x_order'])
        df = df.loc[df['x'].str.contains(classes), :]
        logger.info('Filter on: [%s]' %(classes))

    # Color on values and cmap (after cleaning and filtering)
    if color is None:
        df['color'] = colourmap.fromlist(df['y'].values, scheme='hex', cmap=config['cmap'])[0]

    df.reset_index(inplace=True, drop=True)
    logger.info('Number of samples: %d' %(df.shape[0]))
    return df


def show(df, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    config : dict
        Dictionary containing configuration keys.
    node_properties : dict
        Dictionary containing hex colorlabels for the classes.
        The node_properties are derived using the function: node_properties = d3.set_label_properties()

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    config = kwargs.get('config')
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)

    # Convert dict/frame.
    node_properties = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df, frame=True)

    spacing = 0.10
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        y_spacing = (df['y'].max() - df['y'].min()) * spacing
        config['ylim'] = [df['y'].min() - y_spacing, df['y'].max() + y_spacing]
    # Ordering the class node_properties
    if config['x_order'] is None:
        config['x_order'] = str([*node_properties.keys()])
    if config['figsize'][0] is None:
        config['figsize'][0] = len(node_properties.keys()) * 95
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
    write_html(X, config, logger)
    # Return config
    return config


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
        'WIDTH_FIG': config['figsize'][0],
        'HEIGHT_FIG': config['figsize'][1],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.violin', package_path='d3js'))

    index_template = jinja_env.get_template('violin.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        if logger is not None: logger.info('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


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
    X = df[['x', 'y', 'color', 'size', 'stroke', 'opacity', 'tooltip']].to_json(orient='records')
    # Return
    return X
