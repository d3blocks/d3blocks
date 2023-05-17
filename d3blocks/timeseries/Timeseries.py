"""Timeseries block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import colourmap
from ismember import ismember
import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, set_labels, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='timeseries'
    config['title'] = kwargs.get('title', 'Timeseries - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'timeseries.html'), logger)
    config['figsize'] = kwargs.get('figsize', [1200, 500])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['fontsize'] = kwargs.get('fontsize', 10)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['whitelist'] = kwargs.get('whitelist', None)
    config['sort_on_date'] = kwargs.get('sort_on_date', True)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['datetime'] = kwargs.get('datetime', 'datetime')
    config['dt_format'] = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    config['columns'] = kwargs.get('columns', {'datetime': config['datetime']})
    config['notebook'] = kwargs.get('notebook', False)
    # return
    return config


# %% Get unique labels
# def set_labels(labels, logger=None):
#     """Set unique labels."""
#     if isinstance(labels, pd.DataFrame):
#         if logger is not None: logger.info('Collecting labels from DataFrame using the "source" and "target" columns.')
#         labels = labels.columns.values

#     # Preprocessing
#     labels = pre_processing(labels)

#     # Checks
#     if (labels is None) or len(labels)<1:
#         raise Exception(logger.error('Could not extract the labels!'))

#     # Get unique categories without sort
#     indexes = np.unique(labels, return_index=True)[1]
#     uilabels = np.array([labels[index] for index in sorted(indexes)])
#     # Return
#     return uilabels


# %% Filter labels using whitelist
def _clean_on_whitelist(labels, whitelist=None, datetime=None, logger=None):
    labels = np.array(labels)
    # Keep only whitelist and remove datetime
    # Remove datetime
    if (datetime is not None) and np.any(np.isin(labels, datetime)):
        if logger is not None: logger.info('Removing [%s] from labels.' %(datetime))
        Ikeep = list(map(lambda x: datetime.lower() in x.lower(), labels))
        labels = labels[~np.isin(labels, datetime)]

    if whitelist is not None:
        if logger is not None: logger.info('Filtering columns on: [%s]' %(whitelist))
        Ikeep = list(map(lambda x: x in whitelist, labels))
        labels = labels[Ikeep]
    return labels


# %% Node properties
def set_node_properties(df, **kwargs):
    """Set the node properties for the Timeseries block.

    Parameters
    ----------
    df : array-like or list
        Name of the nodes/links.
    datetime : str, (default: 'datetime')
        Column name that contains the datetime.
    whitelist : str, (Default: None)
        Keep only columns containing this (sub)string (case insensitive)
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    cmap = kwargs.get('cmap', 'Set1')
    datetime = kwargs.get('datetime', 'datetime')
    whitelist = kwargs.get('whitelist', None)
    logger = kwargs.get('logger', None)
    labels = kwargs.get('labels', df)

    # Set unique labels
    uilabels = set_labels(labels, logger=logger)

    # Keep only whitelist and remove datetime
    uilabels = _clean_on_whitelist(uilabels, whitelist, datetime, logger)

    # Create unique label/node colors
    colors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex', verbose=0)
    # Make dict
    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i, 'label': label, 'color': colors[i]}
    # Return
    return dict_labels


# %% Set Edge properties
def set_edge_properties(df, **kwargs):
    """Set the edge properties for the Timeseries block.

    Parameters
    ----------
    df : Input data, pd.DataFrame()
        Input data.
    datetime : str, (default: 'datetime')
        Column name that contains the datetime.
    dt_format : str
        '%d-%m-%Y %H:%M:%S'
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    df : pd.DataFrame()
        Processed dataframe.

    """
    df=df.copy()
    datetime = kwargs.get('datetime', 'datetime')
    dt_format = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    node_properties = kwargs.get('node_properties', None)
    logger = kwargs.get('logger', None)
    node_properties = convert_dataframe_dict(node_properties, frame=False)

    # Get datetime
    if datetime is None:
        if logger is not None: logger.info('Set index for datetime.')
        df.index = pd.to_datetime(df.index.values, format=dt_format)
    elif not np.isin(datetime, df.columns):
        raise Exception('[%s] does not exists.' %(datetime))
    else:
        df.index = pd.to_datetime(df[datetime].values, format=dt_format)
        df.drop(labels=datetime, axis=1, inplace=True)

    if node_properties is not None:
        labels = [*node_properties.keys()]
        idx, _ = ismember(df.columns, labels)
        if ~np.any(idx): df = df.loc[:, idx]

    if df.shape[1]==0:
        if logger is not None: logger.info('All columns are removed. Change whitelist/blacklist setting.')
        return None
    return df


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
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    df = df.copy()
    labels = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)
    config = config.copy()

    # Convert dict/frame.
    labels = convert_dataframe_dict(labels, frame=False)

    # Format for datetime in javascript
    config['dt_format_js'] = '%Y%m%d'
    # Sort on date
    if config['sort_on_date']:
        df.sort_index(inplace=True)

    df_labels = pd.DataFrame(labels).T
    Iloc, idx = ismember(df.columns, df_labels.index.values)
    config['color'] = '"' + str('","'.join(df_labels['color'].iloc[idx].values.astype(str))) + '"'

    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=False)
    df['index'] = df['index'].dt.strftime(config['dt_format_js'])
    df.rename(columns={"index": "date"}, errors="raise", inplace=True)

    # make dataset for javascript
    vals = df.to_string(header=True, index=False, index_names=False).split('\n')
    X = [';'.join(ele.split()) for ele in vals]

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
    content = {
        'json_data': X,
        'COLOR': config['color'],
        'TITLE': config['title'],
        'FONTSIZE': str(config['fontsize']) + 'px',
        'DT_FORMAT': config['dt_format_js'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'SUPPORT': config['support'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.timeseries', package_path='d3js'))

    index_template = jinja_env.get_template('timeseries.html.j2')
    # index_file = Path(config['filepath'])
    # # index_file.write_text(index_template.render(content))
    # if config['overwrite'] and os.path.isfile(index_file):
    #     if logger is not None: logger.info('File already exists and will be overwritten: [%s]' %(index_file))
    #     os.remove(index_file)
    #     time.sleep(0.5)
    # with open(index_file, "w", encoding="utf-8") as f:
    #     f.write(index_template.render(content))

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html
