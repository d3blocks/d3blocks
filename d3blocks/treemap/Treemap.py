"""Treemap block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import json
from jinja2 import Environment, PackageLoader

try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, vec2flare
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, vec2flare


# %% Set configuration properties
def set_config(config={}, margin={}, font={}, border={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] ='treemap'
    config['title'] = kwargs.get('title', 'Treemap - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'treemap.html'), logger)
    config['figsize'] = kwargs.get('figsize', [1000, 600])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['margin'] = {**{"top": 40, "right": 10, "bottom": 10, "left": 10}, **margin}
    config['font'] = {**{'size': 10, 'type': 'sans-serif', 'position': 'absolute'}, **font}
    config['border'] = {**{'type': 'solid', 'color': '#FFFFFF', 'width': 1}, **border}
    config['notebook'] = kwargs.get('notebook', False)
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
    # node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    df = df.copy()
    df = pre_processing(df, labels=df.columns.values[:-1].astype(str))
    # Create unique dataframe, udpate weights
    # df = create_unique_dataframe(df, logger=logger)
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
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i, 'label': label}
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
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    node_properties = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df.copy(), frame=True)

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)

    # Create the data from the input of javascript
    # X = get_data_ready_for_d3(df)
    X = vec2flare(df, logger=logger)

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
    # Set width and height to screen resolution if None.
    width = 'window.screen.width' if config['figsize'][0] is None else config['figsize'][0]
    height = 'window.screen.height' if config['figsize'][1] is None else config['figsize'][1]

    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': width,
        'HEIGHT': height,
        'bordertype': config['border']['type'],
        'bordercolor': config['border']['color'],
        'borderwidth': config['border']['width'],
        'fontsize': config['font']['size'],
        'fonttype': config['font']['type'],
        'fontposition': config['font']['position'],
        'marginTop': config['margin']['top'],
        'marginRight': config['margin']['right'],
        'marginBottom': config['margin']['bottom'],
        'marginLeft': config['margin']['left'],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.treemap', package_path='d3js'))

    index_template = jinja_env.get_template('treemap.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


def get_data_ready_for_d3_simple(df):
    # https://github.com/andrewheekin/csv2flare.json/blob/master/csv2flare.json.py
    # start a new flare.json document
    d = dict()
    d = {"name":"flare", "children": []}
    
    for line in df.values:
        the_parent = line[0]
        the_child = line[1]
        child_size = line[2]
    
        # make a list of keys
        keys_list = []
        for item in d['children']:
            keys_list.append(item['name'])
    
        # if 'the_parent' is NOT a key in the flare.json yet, append it
        if not the_parent in keys_list:
            d['children'].append({"name":the_parent, "children":[{"name":the_child, "size":child_size}]})
    
        # if 'the_parent' IS a key in the flare.json, add a new child to it
        else:
            d['children'][keys_list.index(the_parent)]['children'].append({"name":the_child, "size":child_size})
    
    return d


# def get_data_ready_for_d3_v3(df, labels):
#     data = {"name": "data", "children": []}
#     source_nodes = list(set(df['source']))
#     target_nodes = list(set(df['target']))
#     nodes = sorted(list(set(source_nodes + target_nodes)))

#     for node in nodes:
#         children = []
#         node_df = df[(df['source'] == node) | (df['target'] == node)]
#         node_sources = list(set(node_df['source']))
#         node_targets = list(set(node_df['target']))
#         node_children = sorted(list(set(node_sources + node_targets)))

#         for child in node_children:
#             child_df = node_df[(node_df['source'] == child) | (node_df['target'] == child)]
#             child_weight = sum(child_df['weight'])
#             children.append({"name": child, "size": child_weight})

#         data['children'].append({"name": node, "children": children})

#     # Return
#     return data
