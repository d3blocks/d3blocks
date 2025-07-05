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
import os

try:
    from .. utils import set_path, set_labels, write_html_file, pre_processing, update_config, vec2adjmat, scale, normalize, include_save_to_svg_script
except:
    from utils import set_path, set_labels, write_html_file, pre_processing, update_config, vec2adjmat, scale, normalize, include_save_to_svg_script


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Heatmap'
    config['title'] = kwargs.get('title', 'Heatmap - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'heatmap.html'), logger)
    config['figsize'] = kwargs.get('figsize', [720, 720])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['color'] = kwargs.get('color', 'cluster')
    config['description'] = kwargs.get('description', '')
    config['stroke'] = kwargs.get('stroke', 'red')
    config['notebook'] = kwargs.get('notebook', False)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['cluster_params'] = kwargs.get('cluster_params', {})
    config['scale'] = kwargs.get('scale', False)
    config['fontsize'] = kwargs.get('fontsize', 10)
    config['fontsize_mouseover'] = kwargs.get('fontsize_mouseover', config['fontsize'] + 8)
    config['scaler'] = kwargs.get('scaler', 'zscore')
    config['save_button'] = kwargs.get('save_button', True)

    if config['description'] is None: config['description']=''
    if config['cmap'] in ['schemeCategory10', 'schemeAccent', 'schemeDark2', 'schemePaired', 'schemePastel2', 'schemePastel1', 'schemeSet1', 'schemeSet2', 'schemeSet3', 'schemeTableau10']:
        config['cmap_type']='scaleOrdinal'
    else:
        config['cmap_type']='scaleSequential'

    # return
    return config


def show(df, **kwargs):
    """Build and show the graph."""
    df = df.copy()
    node_properties = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Rescale data
    if df.get('weight', None) is not None:
        df['weight'] = normalize(df['weight'].values, scaler=config['scaler'])

    # Prepare the data
    json_data = get_data_ready_for_d3(df, node_properties)
    # Create the html file
    html = write_html(json_data, config, logger)
    # Return html
    return html


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
    # logger = kwargs.get('logger', None)
    # config = kwargs.get('config')

    df = df.copy()
    df = pre_processing(df)

    return df


# %% Node properties
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
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    logger = kwargs.get('logger', None)
    col_labels = kwargs.get('labels', ['source', 'target'])

    # Get unique labels
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    # Create unique label/node colors
    # cmap = kwargs.get('cmap')
    # colors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex', verbose=0)

    # Make dict
    dict_labels = {}
    for i, label in enumerate(uilabels):
        # dict_labels[label] = {'id': i, 'label': label, 'color': colors[i]}
        dict_labels[label] = {'id': i, 'label': label, 'color': '#000000'}
    # Return
    return dict_labels


def set_colors(df, **kwargs):
    """Color in clusterlabel.

    Returns
    -------
    df : array-like
        Node properties.

    """
    logger = kwargs.get('logger', None)
    config = kwargs.get('config')
    node_properties = kwargs.get('node_properties')

    # d3network.vec2adjmat(source, target, weight=weight, symmetric=symmetric, aggfunc=aggfunc)
    if df.get('weight', None) is not None:
        df = df.copy()
        df['weight'] = normalize(df['weight'].values, scaler=config['scaler'])
    adjmat = vec2adjmat(source=df['source'], target=df['target'], weight=df.get('weight', None).values, symmetric=True)

    # Default is all cluster labels are the same
    # Convert NumPy integers to regular Python integers for proper JSON serialization
    node_properties['classlabel'] = [0] * node_properties.shape[0]
    node_properties['color'] = '#000000'

    if isinstance(config['color'], str) and config['color']=='cluster':
        # Cluster the nodes
        try:
            from clusteval import clusteval
        except:
            raise Exception('clusteval needs to be pip installed first. Tip: pip install clusteval')
        # Initialize
        plot_param = config['cluster_params'].pop('plot', False)
        ce = clusteval(**config['cluster_params'])
        results = ce.fit(adjmat.values)
        if plot_param: ce.plot()
        logger.info('[%d] clusters detected' %(len(np.unique(results['labx']))))

        # uilabx = np.unique(results['labx'])
        Iloc, idx = ismember(node_properties['label'].values, adjmat.index.values)
        if np.any(~Iloc):
            logger.error('Feature name(s): %s can not be used. Hint: Remove special characters. <return>' %(df.index.values[~np.isin(np.arange(0, df.shape[0]), idx)]))
            return None
        logger.info('Colors are based on clustering.')
        # Convert NumPy integers to regular Python integers for proper JSON serialization
        node_properties['classlabel'] = [int(x) for x in results['labx']]
        # # Create node colors
        colors = colourmap.fromlist(node_properties['classlabel'], cmap=config['cmap'], scheme='hex', verbose=0)[0]
        # Convert NumPy strings to regular Python strings
        node_properties['color'] = [str(c) for c in colors]
    elif isinstance(config['color'], (list, np.ndarray)):
        if np.all(list(map(colourmap.is_hex_color, config['color']))):
            logger.info('Colors are based on the input hex colors.')
            # Convert NumPy strings to regular Python strings
            node_properties['color'] = [str(c) for c in config['color']]
            class_labels = ismember(config['color'], np.unique(config['color']))[1]
            node_properties['classlabel'] = [int(x) for x in class_labels]
        else:
            logger.info('Colors are based on the labels.')
            class_labels = ismember(config['color'], np.unique(config['color']))[1]
            node_properties['classlabel'] = [int(x) for x in class_labels]
            colors = colourmap.fromlist(node_properties['classlabel'], cmap=config['cmap'], scheme='hex', verbose=0)[0]
            # Convert NumPy strings to regular Python strings
            node_properties['color'] = [str(c) for c in colors]

    return node_properties


def write_html(json_data, config, logger=None):
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

    # Check path
    dirpath, filename = None, ''
    if config['filepath'] is not None:
        dirpath, filename = os.path.split(config['filepath'])

    # Get path to files
    d3_script = os.path.abspath(os.path.join(config['curpath'], 'heatmap/d3js/heatmap.html.j2'))
    # Import in the file
    with open(d3_script, 'r', encoding="utf8", errors='ignore') as file: html = file.read()

    # Read the d3 html with script file
    html = html.replace('$DESCRIPTION$', str(config['description']))
    html = html.replace('$TITLE$', str(config['title']))
    html = html.replace('$WIDTH$', str(config['figsize'][0]))
    html = html.replace('$WIDTH_DROPDOWN$', str(int(config['figsize'][0] + 200)))
    html = html.replace('$HEIGHT$', str(config['figsize'][1]))
    html = html.replace('$STROKE$', str(config['stroke']))
    html = html.replace('$FONTSIZE$', str(config['fontsize']))
    html = html.replace('$FONTSIZE_MOUSEOVER$', str(config['fontsize_mouseover']))
    html = html.replace('$DATA_PATH$', filename)
    html = html.replace('$SUPPORT$', config['support'])
    html = html.replace('$SAVE_TO_SVG_SCRIPT$', save_script)
    html = html.replace('$SAVE_BUTTON_START$', show_save_button[0])
    html = html.replace('$SAVE_BUTTON_STOP$', show_save_button[1])
    html = html.replace('$DATA_COMES_HERE$', json_data)

    # Write to html
    write_html_file(config, html, logger)
    # Return html
    return html


def get_data_ready_for_d3(df, node_properties):
    """Convert the source-target data into d3 compatible data.

    Embed the Data in the HTML. Note that the embedding is an important stap te prevent security issues by the browsers.
    Most (if not all) browser do not accept to read a file using d3.csv or so. It then requires security-by-passes, but thats not the way to go.
    An alternative is use local-host and CORS but then the approach is not user-friendly coz setting up this, is not so straightforward.
    It leaves us by embedding the data in the HTML. Thats what we are going to do here.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    labels : dict
        Dictionary containing hex colorlabels for the classes.
        The labels are derived using the function: labels = d3blocks.set_label_properties()

    Returns
    -------
    json_data : str.
        Converted data into a string that is d3 compatible.

    """
    # Convert into adj into vector
    dfvec = df.copy()
    uinode, idx = np.unique(node_properties['label'], return_index=True)
    
    # Create a mapping dictionary to avoid FutureWarning about downcasting
    node_to_idx = {}
    for node, i in zip(uinode, idx):
        node_to_idx[node] = int(i)
    
    # Apply the mapping to avoid pandas replace warnings
    # Convert to object dtype first to avoid downcasting warnings
    dfvec['source'] = dfvec['source'].astype('object')
    dfvec['target'] = dfvec['target'].astype('object')
    
    # Now apply the mapping
    dfvec['source'] = dfvec['source'].map(node_to_idx).fillna(dfvec['source'])
    dfvec['target'] = dfvec['target'].map(node_to_idx).fillna(dfvec['target'])
    
    # Ensure proper data types
    dfvec = dfvec.infer_objects(copy=False)

    NODE_STR = '\n{\n"nodes":\n[\n'
    # for node, classlabel in zip(node_properties['label'], node_properties['classlabel']):
    for i, node in enumerate(node_properties['label']):
        # Convert NumPy integers to regular Python integers for proper JSON serialization
        cluster_val = int(node_properties['classlabel'].iloc[i])
        color_val = str(node_properties['color'].iloc[i])
        NODE_STR = NODE_STR + '{"name":' + '"' + node + '"' + ',' + '"cluster":' + str(cluster_val) + ',' + '"color":' + '"' + color_val + '"' + "},"
        # NODE_STR = NODE_STR + '{"name":' + '"' + node + '"' + ',' "},"
        NODE_STR = NODE_STR + '\n'
    NODE_STR = NODE_STR + '],\n'

    EDGE_STR = '"links":\n[\n'
    for i in range(0, dfvec.shape[0]):
        # Convert NumPy integers to regular Python integers for proper JSON serialization
        source_val = int(dfvec.iloc[i, 0])
        target_val = int(dfvec.iloc[i, 1])
        value_val = float(dfvec.iloc[i, 2]) if dfvec.iloc[i, 2] is not None else 0.0
        EDGE_STR = EDGE_STR + '{"source":' + str(source_val) + ',' + '"target":' + str(target_val) + ',' + '"value":' + str(value_val) + '},'
        EDGE_STR = EDGE_STR + '\n'
    EDGE_STR = EDGE_STR + ']\n}'

    # Final data string
    json_data = NODE_STR + EDGE_STR

    # Read the data
    # {
    #   "nodes":
    #       [
    #           {"name":"Name A","cluster":1},
    #           {"name":"Name B","cluster":2},
    #           {"name":"Name C","cluster":2},
    #           {"name":"Name D","cluster":3},
    #           ],
    #       "links":
    #       [
    #           {"source":0,"target":1,"value":1},
    #           {"source":2,"target":2,"value":1},
    #           {"source":3,"target":1,"value":1},
    #       ]
    #   }

    # Check path
    return json_data
