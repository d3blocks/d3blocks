"""Utils.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

from ismember import ismember
import numpy as np
import pandas as pd
import colourmap
import unicodedata
import os
import tempfile
from pathlib import Path
import time
import json
import d3graph as d3network
from collections import defaultdict


def convert_to_json_format(df, logger):
    logger.debug("Setting up json data file..")
    json = []
    for index, row in df.iterrows():
        link = row.astype(str).to_dict()
        json.append(link)
    return json


def is_circular(df, logger=None):
    iloc = df['source'].str.lower()==df['target'].str.lower()
    if np.any(iloc):
        if logger is not None: logger.warning('Data contains self-link that is not allowed\n%s' %(df.loc[iloc, :]))
        return False

    graph = defaultdict(list)
    for _, row in df.iterrows():
        graph[row['source']].append(row['target'])

    visited = set()
    path = set()

    def visit(vertex):
        visited.add(vertex)
        path.add(vertex)
        for neighbour in graph[vertex]:
            if neighbour not in visited:
                if visit(neighbour):
                    return True
            elif neighbour in path:
                return True
        path.remove(vertex)
        return False

    return any(visit(v) for v in list(graph))  # Create a list of the dictionary keys


def adjmat2vec(df, min_weight=1):
    """Convert adjacency matrix into vector with source and target.

    Parameters
    ----------
    adjmat : pd.DataFrame()
        Adjacency matrix.

    min_weight : float
        edges are returned with a minimum weight.

    Returns
    -------
    pd.DataFrame()
        nodes that are connected based on source and target

    Examples
    --------
    >>> # Initialize
    >>> d3 = D3Blocks()
    >>> #
    >>> # Load example
    >>> df = d3.import_example('energy')
    >>> Convert into adjmat
    >>> adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])
    >>> #
    >>> # Convert back to vector
    >>> vector = d3.adjmat2vec(adjmat)

    """
    return d3network.adjmat2vec(df, min_weight=min_weight)


def vec2adjmat(source, target, weight=None, symmetric=True, aggfunc='sum'):
    """Convert source and target into adjacency matrix.

    Parameters
    ----------
    source : list
        The source node.
    target : list
        The target node.
    weight : list of int
        The Weights between the source-target values
    symmetric : bool, optional
        Make the adjacency matrix symmetric with the same number of rows as columns. The default is True.
    aggfunc : str, optional
        Aggregate function in case multiple values exists for the same relationship.
            * 'sum' (default)

    Returns
    -------
    pd.DataFrame
        adjacency matrix.

    Examples
    --------
    >>> # Initialize
    >>> d3 = D3Blocks()
    >>> #
    >>> # Load example
    >>> df = d3.import_example('energy')
    >>> #
    >>> # Convert to adjmat
    >>> adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])

    """
    return d3network.vec2adjmat(source, target, weight=weight, symmetric=symmetric, aggfunc=aggfunc)


# %% Normalize.
def normalize(X, minscale = 0.5, maxscale = 4, scaler: str = 'zscore'):
    # Instead of Min-Max scaling, that shrinks any distribution in the [0, 1] interval, scaling the variables to
    # Z-scores is better. Min-Max Scaling is too sensitive to outlier observations and generates unseen problems,

    # Set sizes to 0 if not available
    X[np.isinf(X)]=0
    X[np.isnan(X)]=0
    if minscale is None: minscale=0.5

    # out-of-scale datapoints.
    if scaler == 'zscore' and len(np.unique(X)) > 3:
        X = (X.flatten() - np.mean(X)) / np.std(X)
        X = X + (minscale - np.min(X))
    elif scaler == 'minmax':
        try:
            from sklearn.preprocessing import MinMaxScaler
        except:
            raise Exception('sklearn needs to be pip installed first. Try: pip install scikit-learn')
        # scaling
        if len(X.shape)<=1: X = X.reshape(-1, 1)
        X = MinMaxScaler(feature_range=(minscale, maxscale)).fit_transform(X).flatten()
    else:
        X = X.ravel()
    # Max digits is 4
    X = np.array(list(map(lambda x: round(x, 4), X)))

    return X


# %% Normalize between [0-1]
def normalize_between_0_and_1(X):
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    out = (X - x_min) / (x_max - x_min)
    out[np.isnan(out)]=1
    return out


# %% Jitter
def jitter_func(x, jitter=0.01):
    """Add jitter to data.

    Noise is generated from random normal distribution and added to the data.

    Parameters
    ----------
    x : numpy array
        input data.
    jitter : float, optional
        Strength of generated noise. The default is 0.01.

    Returns
    -------
    x : array-like
        Data including noise.

    """
    if jitter is None or jitter is False: jitter=0
    if jitter is True: jitter=0.01
    if jitter>0 and x is not None:
        x = x + np.random.normal(0, jitter, size=len(x))
    return x


def vec2flare_v2(df, node_properties=None, chart=None, logger=None):
    # Create the dataframe
    # data = {
    #     'source': ['Klaas', 'Klaas', 'Bill', 'Bill', 'Bill', 'Ana', 'Ana'],
    #     'target': ['Bill', 'Ana', 'Claudette', 'Danny', 'Erika', 'Bill', 'Larry'],
    #     'weight': [1, 1, 1, 1, 1, 1, 1]
    # }
    # df = pd.DataFrame(data)
    
    # Function to recursively build the nested structure
    def build_node(df, name, node_properties=None, visited=None):
        if visited is None:
            visited = set()
        if name in visited:
            return None  # or handle cycle appropriately
        visited.add(name)

        if node_properties.get(name, None) is None:
            color="#D33F6A"
            size=10
            tooltip=name
            node_opacity = 0.95
            edge_size = 1
            edge_color = '#000000'
        else:
            color=node_properties.get(name)['color']
            size=node_properties.get(name)['size']
            edge_size=node_properties.get(name)['edge_size']
            edge_color=node_properties.get(name)['edge_color']
            node_opacity=node_properties.get(name)['opacity']

            # Correct for tooltip
            if node_properties.get(name)['tooltip']==node_properties.get(name)['label']:
                # Prevent showing the name twice
                tooltip= node_properties.get(name)['tooltip']
            elif node_properties.get(name)['tooltip']=='':
                # In case empty, leave it empty
                tooltip = node_properties.get(name)['tooltip']
            else:
                # Otherwise, append the name to the tooltip
                tooltip=name + '<br>' + node_properties.get(name)['tooltip']

        node = {}
        node['name'] = name
        node['node_color'] = color
        node['node_size'] = size
        node['tooltip'] = tooltip
        node['edge_size'] = edge_size
        node['edge_color'] = edge_color
        node['node_opacity'] = node_opacity

        # children = []
        # sub_df = df[df['source'] == name]
        # for _, row in sub_df.iterrows():
        #     child = build_node(df, row['target'], node_properties)
        #     children.append(child)

        children = []
        sub_df = df[df['source'] == name]
        for _, row in sub_df.iterrows():
            if row['target'] not in visited:
                child = build_node(df, row['target'], node_properties, visited)
                children.append(child)

        if children:
            node['children'] = children

        return node

    # Get the unique source names
    uinames = df['source'].unique()

    # Build the tree structure
    tree = []
    for uiname in uinames:
        node = build_node(df, uiname, node_properties)
        tree.append(node)

    # Convert the tree structure to JSON
    json_data = json.dumps(tree[0], indent=4)
    return json_data


# %% Convert to Flare format
def vec2flare(df, logger=None):
    """Convert to Flare format.

    Converting any one-to-one relationship dataframe to a flare format.
    The dataframe contains categorical-ish columns, in order of hierarchy from left to right.
    The column weight contains a number (float or integer).
    Returns A json flare file suitable for plotting starburst chart in D3


    Parameters
    ----------
    df : DataFrame
        DataFrame containing 2 or more columns.
    logger : logging.Logger, optional
        A logger object to output log messages (optional)

    Returns
    -------
    flare : dictionary
        dictionary in flare format.

    References
    ----------
    * https://stackoverflow.com/questions/59946453/creating-a-flare-json-to-be-used-in-d3-from-pandas-dataframe/65333978#65333978
    * https://github.com/andrewheekin/csv2flare.json/blob/master/csv2flare.json.py
    * https://medium.com/swlh/from-pandas-to-d3-json-and-starburst-charts-44279db32436
    * https://github.com/justinhchae/p2d3/blob/main/p2d3/pandas_to_d3.py
    * https://medium.com/swlh/from-pandas-to-d3-json-and-starburst-charts-44279db32436
    * https://stackoverflow.com/questions/11088303/how-to-convert-to-d3s-json-format/11089330#11089330

    """
    # check if 'weight' is the last column
    if df.columns[-1].lower() != 'weight':
        # remove 'weight' column
        value_col = df.pop('weight')
        # add 'weight' column as the last column
        df.insert(len(df.columns), 'weight', value_col)

    flare = {'name': "flare", 'children': []}
    # iterate through dataframe values
    for row in df.values:
        level0 = row[0]
        level1 = row[1]

        if df.shape[1]==3:
            weight = row[-1]
            d = {'name': level0, 'children': [{'name': level1, 'size': weight}]}
        elif df.shape[1]==4:
            level2 = row[2]
            weight = row[-1]
            d = {'name': level0, 'children': [{'name': level1, 'children': [{'name': level2, 'size': weight}]}]}
        # elif df.shape[1]==5:
        #     level2, level3 = row[2], row[3]
        #     weight = row[-1]
        #     d = {'name': level0, 'children': [{'name': level1, 'children': [{'name': level2, 'children': [{'name': level3, 'size': weight}]}]}]}
        # elif df.shape[1]==6:
        #     level2, level3, level4 = row[2], row[3], row[4]
        #     weight = row[-1]
        #     d = {'name': level0, 'children': [{'name': level1, 'children': [{'name': level2, 'children': [{'name': level3, 'children': [{'name': level4, 'size': weight}]}]}]}]}

        # initialize key lists
        key0, key1 = [], []

        # iterate through first level node names
        for i in flare['children']:
            key0.append(i['name'])

            # iterate through next level node names
            key1 = []
            for _, v in i.items():
                if isinstance(v, list):
                    for x in v:
                        key1.append(x['name'])

        # add the full path of data if the root is not in key0
        if level0 not in key0:
            flare['children'].append(d)
        elif level1 not in key1:
            # if the root exists, then append to its children
            # if level1 not in key1:
            flare['children'][key0.index(level0)]['children'].append(d)
        else:
            # if the root exists, then append to its children
            d = {'name': level2, 'size': weight}
            flare['children'][key0.index(level0)]['children'][key1.index(level1)]['children'].append(d)

    if logger is not None: logger.debug(json.dumps(flare, indent=2))
    return flare


# %% Convert the flare into soure-target dataframe
def convert_flare2source_target(filepath):
    """Convert data set into source-target-weights.

    Parameters
    ----------
    filepath : str
        Path to filename containing data.

    Returns
    -------
    pd.DataFrame
        Dataframe containing source,target,weights with the relationships.

    """
    def parse_node(node, parent=None):
        results = []
        name = node['name']
        if 'value' in node:
            results.append((parent, name, node['value']))
        if 'children' in node:
            for child in node['children']:
                results.extend(parse_node(child, parent=name))
        return results

    with open(filepath) as f:
        data = json.load(f)

    parsed_data = parse_node(data)

    # with open(filepath+'.csv', 'w') as f:
    #     for line in parsed_data:
    #         f.write(';'.join(str(x) for x in line) + '\n')

    df = pd.DataFrame(parsed_data, columns=['source', 'target', 'weight'])
    return df


# %% Scaling
def scale(X, vmax=100, vmin=None, make_round=True, logger=None):
    """Scale data.

    Scaling in range by X*(100/max(X))

    Parameters
    ----------
    X : array-like
        Input image data.
    verbose : int (default : 3)
        Print to screen. 0: None, 1: Error, 2: Warning, 3: Info, 4: Debug, 5: Trace.

    Returns
    -------
    df : array-like
        Scaled image.

    """
    if (vmax is not None) and (X is not None):
        logger.info('Scaling image between [min-%s]' %(vmax))
        try:
            # Normalizing between 0-100
            # X = X - X.min()
            X = X / X.max().max()
            X = X * vmax
            if make_round:
                X = np.round(X)
            if vmin is not None:
                X = X + vmin
        except:
            logger.warning('Scaling not possible.')

    return X


# %% Get unique labels
def set_labels(df, col_labels=None, logger=None):
    """Set unique labels."""
    if df is None: raise Exception('Input labels must be provided.')
    if isinstance(df, pd.DataFrame) and (col_labels is not None) and np.all(ismember(col_labels, df.columns.values)[0]):
        if logger is not None: logger.info('Collecting labels from DataFrame using the "source" and "target" columns.')
        labels = df[col_labels].values.flatten().astype(str)
    else:
        labels = df

    # Preprocessing
    labels = pre_processing(labels)

    # Checks
    if (labels is None) or len(labels)<1:
        raise Exception(logger.error('Could not extract the labels!'))

    # Get unique categories without sort
    indexes = np.unique(labels, return_index=True)[1]
    uilabels = [labels[index] for index in sorted(indexes)]
    # Return
    return uilabels


# %% Update config
def update_config(kwargs, logger=None):
    """Update configuration file."""
    # Get all user defined parameters.
    config = kwargs.get('config')
    params = np.array([*kwargs.keys()])
    params = params[~np.isin([*kwargs.keys()], ['config', 'node_properties', 'logger'])]
    # Update config file with new user-defined settings
    for p in params:
        getvalue = kwargs.get(p, None)
        # if getvalue is not None:
        if logger is not None: logger.info('Set [%s]: %s' %(p, kwargs.get(p)))
        config[p] = getvalue
    return config


def set_path(filepath='d3blocks.html', logger=None):
    """Set the file path.

    Parameters
    ----------
    filepath : str
        filename and or full pathname.
        * 'd3graph.html'
        * 'c://temp/'
        * 'c://temp/d3graph.html'

    Returns
    -------
    filepath : str
        Path to graph.

    """
    if filepath is None:
        return None

    dirname, filename = os.path.split(filepath)
    # dirname = os.path.abspath(dirname)

    if (filename is None) or (filename==''):
        filename = 'd3blocks.html'

    if (dirname is None) or (dirname==''):
        dirname = os.path.join(tempfile.gettempdir(), 'd3blocks')

    if not os.path.isdir(dirname):
        if logger is not None: logger.info('Create directory: [%s]', dirname)
        os.mkdir(dirname)

    filepath = os.path.abspath(os.path.join(dirname, filename))
    if logger is not None: logger.info("filepath is set to [%s]" %(filepath))
    # Return
    return Path(filepath)


def convert_dataframe_dict(X, frame, chart=None, logger=None):
    """Convert between dataframe and dictionary.

    Parameters
    ----------
    X : containing label information.
        Dataframe of dictionary.
    frame : Bool
        True: Convert to DataFrame.
        False: Convert to dictionary.

    Returns
    -------
    None.

    """
    if (chart is not None) and np.any(np.isin(chart.lower(), ['movingbubbles', 'timeseries'])):
        return X
    elif (chart is not None) and np.any(np.isin(chart.lower(), ['scatter'])):
        return pd.DataFrame(X).T
    elif (chart is not None) and np.any(np.isin(chart.lower(), ['maps'])):
        return pd.DataFrame(X)

    if isinstance(X, dict) and frame:
        if logger is not None: logger.info('Convert to DataFrame.')
        X = pd.DataFrame.from_dict(X, orient='index').reset_index(drop=True)
    elif isinstance(X, pd.DataFrame) and not frame:
        if logger is not None: logger.info('Convert to Dictionary.')
        if np.all(ismember(['source', 'target'], X.columns.values)[0]):
            X.index = X[['source', 'target']]
        else:
            X.index = X['label']
        X = X.to_dict(orient='index')

    return X


# %% Create unique dataframe and update weights
def create_unique_dataframe(X, logger=None):
    """Combine source-target into adjacency matrix with updated weights.

    Parameters
    ----------
    X : DataFrame
        Data frame containing the columns [source, target, weight].
    logger : Object, optional
        Logger object. The default is None.

    Returns
    -------
    X : pd.DataFrame
        Unique adjacency matrix containing with index as source and columns as target labels. Weights are in the matrix.

    """
    # Check whether labels are unique
    if isinstance(X, pd.DataFrame):
        Iloc = ismember(X.columns, ['source', 'target', 'weight'])[0]
        X = X.loc[:, Iloc]
        if 'weight' in X.columns: X['weight'] = X['weight'].astype(float)
        # Groupby values and sum the weights
        X = X.groupby(by=['source', 'target']).sum()
        X.reset_index(drop=False, inplace=True)
    return X


# %% Setup colors
def set_colors(X, c, cmap, c_gradient=None):
    """Set colors for in various blocks.

    Given the size of input data X, and the class labels, return the hex colors.
    This optional is possible in the following blocks:
        * scatter
        * chord
    """
    hexok = False
    # In case only one (c)olor is defined. Set all to this value.
    if isinstance(c, str): c = np.repeat(c, X.shape[0])

    # Check whether the input is hex colors.
    hexok = np.all(list(map(lambda x: ((len(str(x))>0)) and (str(x[0])=='#') and (len(x)==7), c)))

    if hexok:
        # Input is hex-colors thus we do not need to touch the colors.
        labels = np.arange(0, X.shape[0]).astype(str)
        c_hex = c
    else:
        # The input are string-labels and not colors. Lets convert to hex-colors.
        labels = c
        c_hex, _ = colourmap.fromlist(c, cmap=cmap, scheme='hex', method='matplotlib', gradient=c_gradient, verbose=0)

    if (c_gradient is not None):
        c_hex = density_color(X, c_hex, c)

    # Return
    return c_hex, labels


# %% Create gradient based based on the labels.
def density_color(X, colors, labels):
    """Determine the density.

    Given (x,y) coordinates, determine the density. This optional is possible in the following blocks:
        * scatter.

    """
    from scipy.stats import gaussian_kde
    uilabels = np.unique(labels)
    density_colors = np.repeat('#ffffff', X.shape[0])

    if (len(uilabels)!=len(labels)):
        for label in uilabels:
            idx = np.where(labels==label)[0]
            if X.shape[1]==2:
                xy = np.vstack([X[idx, 0], X[idx, 1]])
            else:
                xy = np.vstack([X[idx, 0], X[idx, 1], X[idx, 2]])

            try:
                # Compute density
                z = gaussian_kde(xy)(xy)
                # Sort on density
                didx = idx[np.argsort(z)[::-1]]
            except:
                didx=idx

            # order colors correctly based Density
            density_colors[didx] = colors[idx]
            # plt.figure()
            # plt.scatter(X[didx,0], X[didx,1], color=colors[idx, :])
            # plt.figure()
            # plt.scatter(idx, idx, color=colors[idx, :])
        colors = density_colors

    # Return
    return colors


# %% Pre processing
def pre_processing(df, labels=['source', 'target'], clean_source_target=False, logger=None):
    """Pre-processing of the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    # Create strings from source-target
    if isinstance(df, pd.DataFrame):
        # Add weights if not exists
        if (df.get('source', None) is not None) and (df.get('target', None) is not None) and (df.get('weight', None) is None):
            if logger is not None: logger.info('Create new column with [weights]=1')
            df['weight']=1

        for label in labels:
            df[label] = df[label].astype(str)
    else:
        if isinstance(df, list):
            df = np.array(df)
        df = df.astype(str)

    # Remove quotes and special chars
    df = remove_quotes(df)
    df = remove_special_chars(df, clean_source_target=clean_source_target)
    df = trim_spaces(df)
    return df


# %% Remove quotes.
def remove_quotes(df):
    """Pre-processing of the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    if isinstance(df, pd.DataFrame):
        Iloc = df.dtypes==object
        df.loc[:, Iloc] = df.loc[:, Iloc].apply(lambda s: s.str.replace("'", ""))
        try:
            if not pd.api.types.is_numeric_dtype(df.index):
                df.columns = np.array(list(map(lambda x: x.replace("'", ""), df.columns)))
            if not pd.api.types.is_numeric_dtype(df.index):
                df.index = np.array(list(map(lambda x: x.replace("'", ""), df.index)))
            if np.all(np.isin(['source', 'target'], df.columns.values)):
                df['source'] = list(map(lambda x: x.replace("'", ""), df['source']))
                df['target'] = list(map(lambda x: x.replace("'", ""), df['target']))
        except:
            pass
        return df
    else:
        return np.array(list(map(lambda x: x.replace("'", ""), df)))


# %% Remove special characters from column names
def trim_spaces(df):
    """Trim spaces at the start and end of strings in the 'source' and 'target' columns."""
    if isinstance(df, pd.DataFrame):
        if df.get('source', None) is not None:
            df['source'] = df['source'].str.strip()
        if df.get('target', None) is not None:
            df['target'] = df['target'].str.strip()
    return df


# %% Remove special characters from column names
def remove_special_chars(df, clean_source_target=False):
    """Remove special characters.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    if isinstance(df, pd.DataFrame):
        df.columns = clean_text(df.columns.values.astype(str))
        df.index = clean_text(df.index.values.astype(str))
        # df.columns = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.columns.values.astype(str)))
        # df.index = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.index.values.astype(str)))

    if isinstance(df, pd.DataFrame) and clean_source_target:
        if df.get('source', None) is not None:
            df['source'] = clean_text(df['source'].values.astype(str))
        if df.get('target', None) is not None:
            df['target'] = clean_text(df['target'].values.astype(str))

    return df


# %% Remove special characters from column names
def clean_text(X):
    return list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), X))


def write_html_file(config, html, logger):
    """Write html file.

    This function writes an HTML file specified in the config dictionary to the file path specified in the 'filepath' key of the config dictionary.
    If the 'overwrite' key of the config dictionary is set to True and the file already exists, the file will be overwritten.
    If a logger object is provided, log messages will be output to the logger.

    Parameters
    ----------
    config : dict
        A dictionary containing the following keys:
            'filepath': (str) The file path to write the HTML file to.
            'overwrite': (bool) If true, existing file will be overwritten.
            'notebook': (bool) If true, the file will not be written.
    html : str
        A string containing the HTML to be written to the file.
    logger : logging.Logger, optional
        A logger object to output log messages (optional)

    Returns
    -------
    None
    """
    index_file = config['filepath']
    if index_file:

        if config['overwrite'] and os.path.isfile(index_file):
            if (logger is not None): logger.info('File already exists and will be overwritten: [%s]' %(index_file))
            os.remove(index_file)
            time.sleep(0.5)

        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html)


def get_support(support):
    script=''
    if isinstance(support, bool) and (not support): support = None
    if isinstance(support, bool) and support: support = 'text'
    if support is not None:
        script="<script async src='https://media.ethicalads.io/media/client/ethicalads.min.js'></script>"
        script = script + '\n' + "<div data-ea-publisher='erdogantgithubio' data-ea-type='{TYPE}' data-ea-style='stickybox'></div>".replace('{TYPE}', support)

    # Return
    return script
