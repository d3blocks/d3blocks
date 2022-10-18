"""Sankey block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
Mail        : erdogant@gmail.com, oliver@sensibly.nl
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing
except:
    from utils import convert_dataframe_dict, set_path, pre_processing


# %% Get unique labels
def set_labels(df):
    return np.unique(df[['source', 'target']].values.flatten())


# %% Set Edge properties
def set_edge_properties(df, node_properties, **kwargs):
    """Set the edge properties."""
    df = pre_processing(df)
    return df


def set_node_properties(labels, cmap, logger, **kwargs):
    """Set the node properties."""
    dict_labels = {}
    for i, label in enumerate(labels):
        dict_labels[label] = {'id': i, 'label': label}
    # Return
    return dict_labels


# %% Set configuration properties
def set_config(config={}, link={}, node={}, margin={}, **kwargs):
    """Set the default configuration setting."""
    # Store configurations
    config['chart'] ='sankey'
    config['title'] = kwargs.get('title', 'Sankey - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'sankey.html'))
    config['figsize'] = kwargs.get('figsize', [800, 600])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['link'] = {**{"color": "source-target", "stroke_opacity": 0.5, "color_static": '#D3D3D3'}, **link}
    config['node'] = {**{"align": "justify", "width": 15, "padding": 15, "color": "currentColor"}, **node}
    config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}
    # return
    return config


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
        The node_properties are derived using the function: node_properties = d3.set_node_properties()

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
    df = convert_dataframe_dict(df.copy(), frame=True)

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)
    df['source_id'] = list(map(lambda x: node_properties.get(x)['id'], df['source']))
    df['target_id'] = list(map(lambda x: node_properties.get(x)['id'], df['target']))

    # Set link_color selection correct on the form
    config['link_color_select'] = {'source': '', 'target': '', 'source-target': ''}
    config['link_color_select'][config['link']['color']] = 'selected="selected"'
    # Set align selection correct on the form
    config['align_select'] = {'left': '', 'right': '', 'justify': '', 'center': ''}
    config['align_select'][config['node']['align']] = 'selected="selected"'

    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df, node_properties)
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
        'link_color': config['link']['color'],
        'link_color_select_source': config['link_color_select']['source'],
        'link_color_select_target': config['link_color_select']['target'],
        'link_color_select_source_target': config['link_color_select']['source-target'],

        'align_select_left': config['align_select']['left'],
        'align_select_right': config['align_select']['right'],
        'align_select_justify': config['align_select']['justify'],
        'align_select_center': config['align_select']['center'],

        'color_static': config['link']['color_static'],
        'link_stroke_opacity': config['link']['stroke_opacity'],
        'marginTop': config['margin']['top'],
        'marginRight': config['margin']['right'],
        'marginBottom': config['margin']['bottom'],
        'marginLeft': config['margin']['left'],
        'node_align': config['node']['align'],
        'node_width': config['node']['width'],
        'node_padding': config['node']['padding'],
        'node_stroke_color': config['node']['color'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.sankey', package_path='d3js'))

    index_template = jinja_env.get_template('sankey.html.j2')
    index_file = Path(config['filepath'])
    if config['overwrite'] and os.path.isfile(index_file):
        if (logger is not None): logger.info('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


def get_data_ready_for_d3(df, labels):
    """Convert the source-target data into d3 compatible data.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    labels : dict
        Dictionary containing hex colorlabels for the classes.
        The labels are derived using the function: labels = d3blocks.set_label_properties()

    Returns
    -------
    X : str.
        Converted data into a string that is d3 compatible.

    """
    # Set the nodes in an increasing id-order
    list_id = np.array(list(map(lambda x: labels.get(x)['id'], df['source'])) + list(map(lambda x: labels.get(x)['id'], df['target'])))
    list_name = np.array(list(map(lambda x: labels.get(x)['label'], df['source'])) + list(map(lambda x: labels.get(x)['label'], df['target'])))
    _, idx = np.unique(list_id, return_index=True)

    # Set the nodes
    X = '{"nodes":['
    for i in idx:
        X = X + '{"name":"' + list_name[i] + '"},'
    X = X[:-1] + '],'

    # Set the links
    # source_target_id = list(zip(list(map(lambda x: labels.get(x)['id'], df['source'])),  list(map(lambda x: labels.get(x)['id'], df['target']))))
    X = X + ' "links":['
    for _, row in df.iterrows():
        X = X + '{"source":' + str(row['source_id']) + ',"target":' + str(row['target_id']) + ',"value":' + str(row['weight']) + '},'
    X = X[:-1] + ']}'

    # Return
    return X
