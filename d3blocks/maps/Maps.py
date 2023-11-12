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

try:
    from .. utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script
except:
    from utils import convert_dataframe_dict, set_path, update_config, write_html_file, convert_to_json_format, include_save_to_svg_script


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
    config['save_button'] = kwargs.get('save_button', True)
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
    opacity = 0.6
    linewidth = 0.5
    line = 'none'
    stroke = '#5A5A5A'

    # Add World if not exist
    if (X is None) or (X.get('World') is None): X.update({'World': {'name': 'World', 'color': color, 'opacity': opacity, 'line': line, 'linewidth': linewidth, 'stroke': stroke}})
    # Add missing values to World
    X['World'] = {**{'name': 'World', 'color': color, 'linewidth': linewidth, 'opacity': opacity, "line": line, 'stroke': stroke}, **X['World']}

    # Color each country and add the following missing values
    opacity = 0.8
    linewidth = 1
    line = 'dashed'

    # Create new dict
    countries = {}
    # Add world key that is used for the properties of the entire map
    countries['World'] = X['World']
    # If countries are manually specified. Check whether all items are present. Update with World items if missing.
    if isinstance(X, dict):
        for key in X.keys():
            countries[key] = {'name': key,
                              'color': X[key].get('color', X['World']['color']),
                              'opacity': X[key].get('opacity', X['World']['opacity']),
                              'linewidth': X[key].get('linewidth', X['World']['linewidth']),
                              'line': X[key].get('line', X['World']['line']),
                              'stroke': X[key].get('stroke', X['World']['stroke']),
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
    cmap = kwargs.get('cmap', 'Set1')

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
    if isinstance(color, str) and cm.is_hex_color(color, verbose=0): color = [color] * len(lon)
    if isinstance(color, (np.ndarray, list)) and not np.all(list(map(lambda c: cm.is_hex_color(c, verbose=0), color))):
        color = cm.fromlist(color.astype(str), cmap=cmap, scheme='hex')[0]

    # Get label
    label = df.get('label', None)
    if label is None: label = kwargs.get('label', None)
    if label is None: label = np.repeat([''], len(lon))
    if isinstance(label, (int, float, str)): label = [label] * len(lon)

    dict_labels = {}
    for i in np.arange(0, df.shape[0]):
        # Store
        dict_labels[i] = {
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
    # Create the data from the input of javascript
    json_countries = convert_to_json_format(countries, logger=logger)

    # Write to HTML
    return write_html(json_countries, json_data, config, logger)

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
    # Save button
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])
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
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
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
