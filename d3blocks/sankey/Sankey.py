"""Sankey block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
Mail        : erdogant@gmail.com, oliver@sensibly.nl
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import numpy as np
from jinja2 import Environment, PackageLoader
import colourmap as cm

try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, is_circular, convert_to_json_format, include_save_to_svg_script
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file, is_circular, convert_to_json_format, include_save_to_svg_script


# %% Set configuration properties
def set_config(config={}, link={}, node={}, margin={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    # Store configurations
    config['chart'] ='sankey'
    config['title'] = kwargs.get('title', 'Sankey - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'sankey.html'), logger)
    config['figsize'] = kwargs.get('figsize', [800, 600])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['link'] = {**{"color": "source-target", "stroke_opacity": 0.5, "color_static": '#d3d3d3'}, **link}
    config['node'] = {**{"align": "justify", "width": 15, "padding": 15, "color": "currentColor"}, **node}
    config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}
    config['notebook'] = kwargs.get('notebook', False)
    config['save_button'] = kwargs.get('save_button', True)
    # return
    return config


# %% Get unique labels
# def set_labels(labels, logger=None):
#     """Set unique labels."""
#     if isinstance(labels, pd.DataFrame) and np.all(ismember(['source', 'target'], labels.columns.values)[0]):
#         if logger is not None: logger.info('Collecting labels from DataFrame using the "source" and "target" columns.')
#         labels = labels[['source', 'target']].values.flatten()

#     # Preprocessing
#     labels = pre_processing(labels)

#     # Checks
#     if (labels is None) or len(labels)<1:
#         raise Exception(logger.error('Could not extract the labels!'))

#     # Get unique categories without sort
#     indexes = np.unique(labels, return_index=True)[1]
#     uilabels = [labels[index] for index in sorted(indexes)]
#     # Return
#     return uilabels


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
    df = pre_processing(df.copy(), clean_source_target=True, logger=logger)
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
    dfO = df.copy()
    df = pre_processing(df.copy(), clean_source_target=True)
    logger = kwargs.get('logger', None)
    cmap = kwargs.get('cmap', 'Set1')

    # Get unique label
    col_labels = kwargs.get('labels', ['source', 'target'])
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    # Get color
    color = df.get('color', None)
    if color is None: color = kwargs.get('color', None)
    if color is not None:
        # Make same changes in the labels for the input nodes
        labels = dict(zip(dfO['source'].values.tolist() + dfO['target'].values.tolist(), df['source'].values.tolist() + df['target'].values.tolist()))
        keys = list(color.keys())
        for key in keys:
            color[labels.get(key)] = color.pop(key)

    dict_labels = {}
    for i, label in enumerate(uilabels):
        getcolor = '#d3d3d3'
        # Change color if user-defined.
        if color is not None:
            getcolor = color.get(label, getcolor)
        # create dict labels
        dict_labels[label] = {'id': i, 'label': label, 'color': getcolor}
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
    # Check whether dataframe is circular
    if is_circular(df, logger):
        logger.warning("The dataframe seems to be circular which can not be handled by this chart!")

    # node_properties = convert_dataframe_dict(node_properties.copy(), frame=True)
    # X_nodes = convert_to_json_format(node_properties, logger=logger)
    uicolors = np.unique(list(map(lambda x: node_properties.get(x)['color'], node_properties.keys())))
    custom_colors = np.any(~np.isin(uicolors, '#d3d3d3'))
    # Write to HTML
    return write_html(X, config, custom_colors, logger)


def write_html(X, config, custom_colors, logger=None):
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

        'CUSTOM_NODE_COLORS': str(custom_colors).lower(),
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

        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.sankey', package_path='d3js'))

    index_template = jinja_env.get_template('sankey.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


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
        X = X + '{"name":"' + list_name[i] + '", "color":"' + labels.get(list_name[i])["color"] + '"},'
    X = X[:-1] + '],'

    # Set the links
    # source_target_id = list(zip(list(map(lambda x: labels.get(x)['id'], df['source'])),  list(map(lambda x: labels.get(x)['id'], df['target']))))
    X = X + ' "links":['
    for _, row in df.iterrows():
        X = X + '{"source":' + str(row['source_id']) + ',"target":' + str(row['target_id']) + ',"value":' + str(row['weight']) + '},'
    X = X[:-1] + ']}'

    # Return
    return X
