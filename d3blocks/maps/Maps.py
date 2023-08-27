"""Maps block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from jinja2 import Environment, PackageLoader
import pandas as pd
import numpy as np

try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] ='maps'
    config['title'] = kwargs.get('title', 'Maps - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'maps.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    if config['figsize'] is None: config['figsize'] = [None, None]
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['notebook'] = kwargs.get('notebook', False)
    # return
    return config


# %% Set Edge properties
def set_edge_properties(X, **kwargs):
    """Set the edge properties.

    Parameters
    ----------
    df : pd.DataFrame()
    logger : Object, (default: None)
        Logger.

    Returns
    -------
    df : pd.DataFrame()
        DataFrame.

    """
    logger = kwargs.get('logger', None)
    color = '#D3D3D3'
    opacity = 0.8
    linewidth = 1
    line = 'dashed'

    # Add World if not exist
    if (X is None) or (X.get('World') is None): X.update({'World': {'label': 'World', 'color': color, 'opacity': opacity, 'line': line, 'linewidth': linewidth}})
    # Add missing values to World
    X['World'] = {**{'label': 'World', 'color': color, 'linewidth': linewidth, 'opacity': opacity, "line": line}, **X['World']}

    countries = {}
    countries['World'] = X['World']

    # If World is the only key: then retrieve all availble countries.
    # if (isinstance(X, dict) and (X.get('World', None) is not None) and len(X.keys())==1):
    #     world = ['Netherlands', 'France']
    #     for key in world:
    #         countries[key] = {'label': key,
    #                           'color': X['World'].get('color', X['World']['color']),
    #                           'opacity': X['World'].get('opacity', X['World']['opacity']),
    #                           'linewidth': X['World'].get('linewidth', X['World']['linewidth']),
    #                           'line': X['World'].get('line', X['World']['line']),
    #                           }
    # If countries are manually specified. Check whether all items are present. Update with World items if missing.
    if isinstance(X, dict):
        for key in X.keys():
            countries[key] = {'label': key,
                              'color': X[key].get('color', X['World']['color']),
                              'opacity': X[key].get('opacity', X['World']['opacity']),
                              'linewidth': X[key].get('linewidth', X['World']['linewidth']),
                              'line': X[key].get('line', X['World']['line']),
                              }

    df = convert_dataframe_dict(countries, frame=True, logger=logger)
    return df


def set_node_properties(df, **kwargs):
    """Set the node properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    # Get unique label
    logger = kwargs.get('logger', None)

    # Get longitude
    lon = df.get('lon', None)
    if lon is None: lon = kwargs.get('lon')
    # Get latitude
    lat = df.get('lat', None)
    if lat is None: lat = kwargs.get('lat')

    # Get size
    size = df.get('size', None)
    if size is None: size = kwargs.get('size', None)
    if size is None: size = np.repeat(10, len(lon))
    if isinstance(size, (int, float)): size = [size] * len(lon)

    # Get opacity
    opacity = df.get('opacity', None)
    if opacity is None: opacity = kwargs.get('opacity', None)
    if opacity is None: opacity = np.repeat([0.8], len(lon))
    if isinstance(opacity, (int, float)): opacity = [opacity] * len(lon)

    # Get color
    color = df.get('color', None)
    if color is None: color = kwargs.get('color', None)
    if color is None: color = np.repeat(['#0981D1'], len(lon))
    if isinstance(color, str): color = [color] * len(lon)

    # Get label
    label = df.get('label', None)
    if label is None: label = kwargs.get('label', None)
    if label is None: label = np.repeat([''], len(lon))
    if isinstance(label, (int, float, str)): label = [label] * len(lon)

    dict_labels = {}
    for i in np.arange(0, df.shape[0]):
        # Store
        dict_labels[i] = {'id': i,
                          'lon': lon[i],
                          'lat': lat[i],
                          'label': label[i],
                          'size': size[i],
                          'color': color[i],
                          'opacity': opacity[i],
                          }
    # Return
    return dict_labels


def show(countries, **kwargs):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    config : dict
        Dictionary containing configuration keys.
    node_properties : dict
        Dictionary containing the node properties.
        The node_properties are derived using the function: node_properties = d3.set_node_properties()

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    node_properties = kwargs.get('node_properties', None)
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert node properties to dict/frame.
    node_properties = convert_dataframe_dict(node_properties, frame=False, chart=config['chart'])
    # Create the data from the input of javascript
    json_data = convert_to_json_format(node_properties, logger=logger)

    # Edge properties: Transform dataframe into input form for d3
    countries = convert_dataframe_dict(countries.copy(), frame=True)
    countries.reset_index(inplace=True, drop=True)
    # countries = countries.rename(columns={'index': 'label'})
    # Create the data from the input of javascript
    json_countries = convert_to_json_format(countries, logger=logger)

    # Write to HTML
    return write_html(json_countries, json_data, config, logger)


def convert_to_json_format(df, logger):
    logger.debug("Setting up scatter point data for map..")
    json = []
    for index, row in df.iterrows():
        link = row.astype(str).to_dict()
        json.append(link)
    return json

# def convert_to_json_format(df, logger):
#     logger.debug("Setting up country data for map..")
#     json = []
#     for index, row in df.iterrows():
#         link = row.to_dict()
#         json.append(link)
#     return json


def write_html(json_countries, json_data, config, logger=None):
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
    # Set width and height to screen resolution if None.
    width = 'window.screen.width' if config['figsize'][0] is None else config['figsize'][0]
    height = 'window.screen.height' if config['figsize'][1] is None else config['figsize'][1]

    content = {
        'json_countries': json_countries,
        'json_data': json_data,
        'TITLE': config['title'],
        'WIDTH': width,
        'HEIGHT': height,
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.maps', package_path='d3js'))

    index_template = jinja_env.get_template('maps.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html
