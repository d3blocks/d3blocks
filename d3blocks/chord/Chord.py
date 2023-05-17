"""Chord block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
Mail        : erdogant@gmail.com, oliver@sensibly.nl
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
from ismember import ismember
import colourmap
import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time

try:
    from .. utils import set_colors, pre_processing, convert_dataframe_dict, set_path, update_config, set_labels, create_unique_dataframe, write_html_file
except:
    from utils import set_colors, pre_processing, convert_dataframe_dict, set_path, update_config, set_labels, create_unique_dataframe, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Chord'
    config['title'] = kwargs.get('title', 'Chord - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'chord.html'), logger)
    config['figsize'] = kwargs.get('figsize', [900, 900])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['cmap'] = kwargs.get('cmap', 'tab20')
    config['fontsize'] = kwargs.get('fontsize', 10)
    config['notebook'] = kwargs.get('notebook', False)
    # return
    return config


def set_node_properties(df, **kwargs):
    """Set the node properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'
    cmap : String, (default: 'tab20')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv','inferno'
    opacity: float [0..1] (default: 0.8)
        Opacity of the edge/link.
        * 0.8: All edges/links have the same opacity.
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    cmap = kwargs.get('cmap', 'tab20')
    opacity = kwargs.get('opacity', 0.8)
    logger = kwargs.get('logger', None)
    col_labels = kwargs.get('labels', ['source', 'target'])

    # Get unique labels
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    # Set opacity properties
    opacity = np.repeat(opacity, len(uilabels))
    # Create unique label/node colors
    colors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex', verbose=0)

    # Make dict
    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i, 'label': label, 'color': colors[i], 'opacity': opacity[i]}
    # Return
    return dict_labels


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
        'color' (optional)
        'opacity' (optional)
        color: (default: 'source')
        Edge colors in Hex notation. Should be the same size as input DataFrame.
        * None : 'cmap' is used to create colors.
        * 'source': Color edges/links similar to that of source-color node.
        * 'target': Color edges/links similar to that of target-color node.
        * 'source-target': Color edges/link based on unique source-target edges using the colormap.
        * '#ffffff': All links have the same hex color.
        * ['#000000', '#ffffff',...]: Define per link.
        opacity: (default: 'source')
        Edge Opacity. Should be the same size as input DataFrame.
        * 'source': Opacity of edges/links similar to that of source-opacity node.
        * 'target': Opacity of edges/links similar to that of target-opacity node.
        * 0.8: All links have the same opacity.
        * [0.1, 0.75,...]: Set opacity per edge/link.
    cmap : String, (default: 'inferno')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
    nodes : dict, (default: None)
        Dictionary containing node properties using the function: d3.node_properties(df). Output is stored in d3.nodes
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    df : pd.DataFrame()
        DataFrame.

    """
    df = df.copy()
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    color = kwargs.get('color', 'source')
    opacity = kwargs.get('opacity', 'source')
    cmap = kwargs.get('cmap', 'tab20')

    # Create unique dataframe, udpate weights
    df = create_unique_dataframe(df, logger=logger)

    # Convert dict/frame.
    df = convert_dataframe_dict(df, frame=True)

    # Convert to dict/frame.
    nodes = convert_dataframe_dict(node_properties, frame=False)
    df = convert_dataframe_dict(df, frame=True)

    if isinstance(opacity, (list, np.ndarray)) and (len(opacity)!=df.shape[0]):
        raise Exception('Input parameter "opacity" should be of same size of dataframe.')
    elif (opacity is None) and np.any(df.columns=='opacity'):
        # Set to dataframe.
        if logger is not None: logger.info('Set edge-opacity using the column "opacity" of the input DataFrame.')
        # opacity = df['opacity'].values
    elif (nodes is not None) and isinstance(opacity, str) and (opacity=='source' or opacity=='target'):
        # Set to source or target node color.
        if logger is not None: logger.info('Set edge-opacity based on the [%s] node-opacity.' %(opacity))
        df['opacity'] = 0.8
        for key in nodes.keys():
            df.loc[df[opacity]==key, 'opacity']=nodes.get(key)['opacity']
    elif isinstance(opacity, (int, float)):
        # In case one opacity is defined.
        if logger is not None: logger.info('Set edge-opacity to [%s].' %(opacity))
        df['opacity'] = opacity
    elif isinstance(opacity, (list, np.ndarray)) and (len(opacity)==df.shape[0]):
        if logger is not None: logger.info('Set edge-opacity to user defined input.')
    else:
        if logger is not None: logger.info('Set edge-opacity to default value (0.8).')
        df['opacity'] = 0.8

    # Pre processing
    df = pre_processing(df)

    # Set colors based on source or target
    if (color is None) and np.any(df.columns=='color'):
        # Set to dataframe.
        if logger is not None: logger.info('Set edge-colors using the column "color" of the input DataFrame.')
        color = df['color'].values
    elif (nodes is not None) and (isinstance(color, str)) and (color=='source' or color=='target'):
        # Set to source or target node color.
        if logger is not None: logger.info('Set edge-colors based on the [%s] node-color.' %(color))
        df['color'] = '#000000'
        for key in nodes.keys():
            df.loc[df[color]==key, 'color'] = nodes.get(key)['color']
    elif isinstance(color, str) and (color[0]=='#') and (len(color)==7):
        # In case one hex color is defined.
        if logger is not None: logger.info('Set all edge-colors to [%s].' %(color))
        df['color'] = np.repeat(color, df.shape[0])
    elif isinstance(color, (list, np.ndarray)) and (len(color)==df.shape[0]):
        if logger is not None: logger.info('Set edge-colors to user defined input.')
    else:
        # Get unique source-target to make sure they get the same color.
        if logger is not None: logger.info('Set edge-colors based on unique source-target pairs.')
        uidf = df.groupby(['source', 'target']).size().reset_index()
        _, df['labels'] = ismember(df[['source', 'target']].values.astype(str), uidf[['source', 'target']].values.astype(str), method='rows')
        df['color'], _ = set_colors(df, df['labels'].values.astype(str), cmap, c_gradient=None)

    # return
    return df


def show(df, **kwargs):
    """Show the Chord chart.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
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
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    df = convert_dataframe_dict(df.copy(), frame=True)
    node_properties = convert_dataframe_dict(node_properties, frame=False)

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)
    df['source_id'] = list(map(lambda x: node_properties.get(x)['id'], df['source']))
    df['target_id'] = list(map(lambda x: node_properties.get(x)['id'], df['target']))
    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df, node_properties)
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
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'FONTSIZE': config['fontsize'],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.chord', package_path='d3js'))

    index_template = jinja_env.get_template('chord.html.j2')

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
        color = labels.get(list_name[i])['color']
        opacity = labels.get(list_name[i])['opacity']
        X = X + '{"name":"' + list_name[i] + '",'
        X = X + '"color":"' + color + '",'
        X = X + '"opacity":' + str(opacity)
        X = X + '}, '
    X = X[:-1] + '],'

    # Set the links
    # source_target_id = list(zip(list(map(lambda x: labels.get(x)['id'], df['source'])),  list(map(lambda x: labels.get(x)['id'], df['target']))))
    X = X + ' "links":['
    for _, row in df.iterrows():
        X = X + '{"source":' + str(row['source_id']) + ',"target":' + str(row['target_id']) + ',"value":' + str(row['weight']) + ',"opacity":' + str(row['opacity']) + ',"color":' + '"' + str(row['color']) + '"' + '},'
    X = X[:-1] + ']}'

    # Return
    return X
