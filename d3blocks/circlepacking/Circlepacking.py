"""Circlepacking block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from jinja2 import Environment, PackageLoader

try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, is_circular, include_save_to_svg_script
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, is_circular, include_save_to_svg_script


# %% Set configuration properties
def set_config(config={}, margin={}, font={}, border={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] ='circlepacking'
    config['title'] = kwargs.get('title', 'Circlepacking - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'circlepacking.html'), logger)
    config['figsize'] = kwargs.get('figsize', [900, 1920])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['speed'] = kwargs.get('speed', 750)
    config['zoom'] = kwargs.get('zoom', 'click')
    config['size'] = kwargs.get('size', 'sum')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['font'] = {**{'size': 20, 'color': '#000000', 'type': 'Source Serif Pro', 'outlinecolor': '#FFFFFF'}, **font}
    config['border'] = {**{'color': '#FFFFFF', 'width': 1.5, 'fill': '#FFFFFF', "padding": 5}, **border}
    config['notebook'] = kwargs.get('notebook', False)
    config['save_button'] = kwargs.get('save_button', True)
    # return
    return config


# %% Set Edge properties
def set_edge_properties(df, **kwargs):
    """Set the edge properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'
        'weight'
    logger : Object, (default: None)
        Logger.

    Returns
    -------
    df : pd.DataFrame()
        DataFrame.

    """
    logger = kwargs.get('logger', None)
    df = df.copy()
    df = pre_processing(df, labels=df.columns.values[:-1].astype(str), logger=logger)
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
    col_labels = kwargs.get('labels', ['source', 'target'])
    logger = kwargs.get('logger', None)
    size = kwargs.get('size')
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    dict_labels = {}
    for i, label in enumerate(uilabels):
        if size=='sum':
            if df.loc[df['source']==label].empty:
                weight = df.loc[df['target']==label]['weight'].sum()
            else:
                weight = df.loc[df['source']==label]['weight'].sum()
        else:
            weight = 1
        # Store
        dict_labels[label] = {'id': i, 'label': label, 'value': weight}
    # Return
    return dict_labels


def show(df, **kwargs):
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
    df = df.copy()
    node_properties = kwargs.get('node_properties', None)
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    node_properties = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df.copy(), frame=True)

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)

    # Create the data from the input of javascript
    # X = vec2flare(df, logger=logger)
    X = convert_to_links_format(df, logger=logger)

    # Check whether dataframe is circular
    if is_circular(df, logger):
        logger.warning("The dataframe contains circularity or self-link which can not be handled by this chart!")

    # Write to HTML
    return write_html(X, config, node_properties, logger)


def convert_to_links_format(df, logger):
    logger.debug("Setting up data for d3js..")
    links = []
    for index, row in df.iterrows():
        link = {"source": row['source'], "target": row['target'], "value": row['weight']}
        links.append(link)
    return links


def write_html(X, config, node_properties, logger=None):
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
        'json_data': X,
        'json_nodes': node_properties,
        'TITLE': config['title'],
        'WIDTH': width,
        'HEIGHT': height,
        'SPEED': config['speed'],
        'ZOOM': config['zoom'],
        'bordercolor': config['border']['color'],
        'borderwidth': config['border']['width'],
        'borderfill': config['border']['fill'],
        'borderpadding': config['border']['padding'],
        'fontsize': config['font']['size'],
        'fontcolor': config['font']['color'],
        'fonttype': config['font']['type'],
        'fontoutlinecolor': config['font']['outlinecolor'],
        'SUPPORT': config['support'],
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.circlepacking', package_path='d3js'))

    index_template = jinja_env.get_template('circlepacking.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html
