"""Timeseries block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

import pandas as pd
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
try:
    from .. utils import convert_dataframe_dict, set_path
except:
    from utils import convert_dataframe_dict, set_path


# %% Set configuration properties
def set_config(config, logger=None):
    """Set the general configuration setting."""
    config['chart'] ='timeseries'
    config['title']='Timeseries - D3blocks'
    config['filepath']=set_path('timeseries.html')
    config['figsize']=[1000, 500]
    config['showfig']=True
    config['overwrite']=True
    config['fontsize']=10
    config['sort_on_date'] = True
    config['columns'] = {'datetime': None}
    return config


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
    # Convert dict/frame.
    labels = convert_dataframe_dict(labels, frame=False)
    df = convert_dataframe_dict(df, frame=True)

    # Format for datetime in javascript
    config['dt_format_js'] = '%Y%m%d'
    # Sort on date
    if config['sort_on_date']:
        df.sort_index(inplace=True)
    # Transform dataframe into input form for d3
    df.reset_index(inplace=True, drop=False)
    df['index'] = df['index'].dt.strftime(config['dt_format_js'])
    df.rename(columns={"index": "date"}, errors="raise", inplace=True)

    # make dataset for javascript
    vals = df.to_string(header=True, index=False, index_names=False).split('\n')
    X = [';'.join(ele.split()) for ele in vals]

    # Set color codes for the d3js
    df_labels = pd.DataFrame(labels).T
    X = [';'.join(ele.split()) for ele in vals]
    # Set color
    config['color'] = '"' + str('","'.join(df_labels['color'].values.astype(str))) + '"'

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
        'COLOR': config['color'],
        'TITLE': config['title'],
        'FONTSIZE': str(config['fontsize']) + 'px',
        'DT_FORMAT': config['dt_format_js'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.timeseries', package_path='d3js'))

    index_template = jinja_env.get_template('timeseries.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))
