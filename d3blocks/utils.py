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


# %% Scaling
def scale(X, vmax=100, make_round=True, logger=None):
    """Scale data.

    Description
    -----------
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
    if vmax is not None:
        logger.info('Scaling image between [min-%s]' %(vmax))
        try:
            # Normalizing between 0-100
            # X = X - X.min()
            X = X / X.max().max()
            X = X * vmax
            if make_round:
                X = np.round(X)
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
    elif (chart is not None) and (chart=='scatter'):
        return pd.DataFrame(X).T

    if isinstance(X, dict) and frame:
        if logger is not None: logger.info('Convert to Frame.')
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

    Description
    -----------
    Given the size of input data X, and the class labels, return the hex colors.
    This optional is possible in the following blocks:
        * scatter
        * chord
    """
    hexok = False
    # In case only one (c)olor is defined. Set all to this value.
    if isinstance(c, str): c = np.repeat(c, X.shape[0])

    # Check whether the input is hex colors.
    hexok = np.all(list(map(lambda x: (x[0]=='#') and (len(x)==7), c)))

    if hexok:
        # Input is hex-colors thus we do not need to touch the colors.
        labels = np.arange(0, X.shape[0]).astype(str)
        c_hex = c
    else:
        # The input are string-labels and not colors. Lets convert to hex-colors.
        labels = c
        c_hex, _ = colourmap.fromlist(c, cmap=cmap, method='matplotlib', gradient=c_gradient, scheme='hex', verbose=0)

    if (c_gradient is not None):
        c_hex = density_color(X, c_hex, c)

    # Return
    return c_hex, labels


# %% Create gradient based based on the labels.
def density_color(X, colors, labels):
    """Determine the density.

    Description
    -----------
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
def pre_processing(df, labels=['source', 'target']):
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
        for col in labels:
            df[col] = df[col].astype(str)
    else:
        if isinstance(df, list):
            df = np.array(df)
        df = df.astype(str)

    # Remove quotes and special chars
    df = remove_quotes(df)
    df = remove_special_chars(df)
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
        except:
            pass
        return df
    else:
        return np.array(list(map(lambda x: x.replace("'", ""), df)))


# %% Remove special characters from column names
def remove_special_chars(df):
    """Remove special characters.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    if isinstance(df, pd.DataFrame):
        df.columns = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.columns.values.astype(str)))
        df.index = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.index.values.astype(str)))
        return df
    else:
        return df

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
