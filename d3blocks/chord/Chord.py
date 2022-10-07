"""Chord block.

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
    from .. utils import set_colors
except:
    from utils import set_colors
from ismember import ismember


# %% Preprocessing
def preprocessing(df, opacity=0.8, c=None, cmap='Set2', logger=None):
    """Preprocessing."""
    # In case only one opacity is defined. Set all points to this size.
    if isinstance(opacity, (int, float)): opacity = np.repeat(opacity, df.shape[0])
    df['opacity'] = opacity
    # colors
    if c is None:
        # Get unique source-target to make sure they get the same color.
        uidf = df.groupby(['source', 'target']).size().reset_index()
        _, df['labels'] = ismember(df[['source', 'target']], uidf[['source', 'target']], method='rows')
        df['color'], _ = set_colors(df, df['labels'].values.astype(str), cmap, c_gradient=None)
    # return
    return df


def show(df, config, labels=None):
    """Build and show the graph.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    config : dict
        Dictionary containing configuration keys.
    labels : dict
        Dictionary containing hex colorlabels for the classes.
        The labels are derived using the function: labels = d3blocks.set_label_properties()

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=True)
    df['source_id'] = list(map(lambda x: labels.get(x)['id'], df['source']))
    df['target_id'] = list(map(lambda x: labels.get(x)['id'], df['target']))
    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df, labels)
    # Write to HTML
    write_html(X, config)
    # Return config
    return config


def write_html(X, config):
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
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.chord', package_path='d3js'))

    index_template = jinja_env.get_template('chord.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
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
    list_name = np.array(list(map(lambda x: labels.get(x)['desc'], df['source'])) + list(map(lambda x: labels.get(x)['desc'], df['target'])))
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
        X = X + '{"source":' + str(row['source_id']) + ',"target":' + str(row['target_id']) + ',"value":' + str(row['weight']) + ',"opacity":' + str(row['opacity']) + ',"color":' + '"' + str(row['color']) + '"' + '},'
    X = X[:-1] + ']}'

    # Return
    return X
