"""Moving bubble graph."""

import numpy as np
import pandas as pd
import re
from tqdm import tqdm
import os
from jinja2 import Environment, PackageLoader
from pathlib import Path


def compute_delta(df, sample_id, datetime):
    """Compute date time delta.

    Description
    -----------
    The input for movingbubbles is the difference between two time points.
    The following steps are taken to compute the delta:
        1. Per sample_id or cases/samples/events do the following:
            a. Sort on datetime
            b. Substract the two following time points.

    Parameters
    ----------
    df : Input dataFrame
        Input data.
    sample_id : list of str.
        Category name.
    datetime : datetime
        date time.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """
    # Use copy of dataframe
    df = df.copy()
    # Initialize empty delta
    df['delta'] = df[datetime] - df[datetime]
    # Sort datetime
    df = df.sort_values(by=datetime)
    df.reset_index(inplace=True, drop=True)
    # Compute per category the delta
    for i in np.unique(df[sample_id]):
        Iloc = df[sample_id]==i
        dftmp = df.loc[Iloc, :]
        df['delta'].loc[Iloc] = dftmp[datetime].iloc[1:].values - dftmp[datetime].iloc[:-1]

    # Set the last event at 0
    Iloc = df['delta'].isna()
    df['delta'].loc[Iloc] = dftmp[datetime].iloc[0] - dftmp[datetime].iloc[0]
    # Return
    return df


def show(df, config, labels=None):
    """Build and show the graph.

    Parameters
    ----------
    X : Input data
        Input data.

    Returns
    -------
    None.

    """
    if not isinstance(df, pd.DataFrame):
        write_html(df, config)
        return config

    if not np.any(df.columns=='delta'):
        raise Exception('Column "delta" is missing in dataFrame of type datetime.')
    if config['center'] is None:
        config['center'] = [*labels.keys()][0]
    # Extract minutes and days
    if config['reset_time']=='day':
        df['time_in_state'] = (np.ceil(df['delta'].dt.seconds / 60)).astype(int)
    elif config['reset_time']=='year':
        df['time_in_state'] = df['delta'].dt.days.astype(int)

    # Transform dataframe into input form for d3
    X = []
    sid = np.array(list(map(lambda x: labels.get(x)['id'], df['category'].values)))
    uiid = np.unique(df['sample_id'])
    for i in uiid:
        Iloc=df['sample_id']==i
        tmplist=str(list(zip(sid[Iloc], df['time_in_state'].loc[Iloc].values)))
        tmplist=tmplist.replace('(','')
        tmplist=tmplist.replace(')','')
        tmplist=tmplist.replace('[','')
        tmplist=tmplist.replace(']','')
        tmplist=tmplist.replace(' ','')
        # Make one big happy list
        X = [tmplist] + X


# 	var colorByActivity = {
# 		"0": "#e0d400",
# 		"1": "#1c8af9",
# 		"2": "#51BC05",
# 		"3": "#FF7F00",
# 		"4": "#DB32A4",
# 		"5": "#00CDF8",
# 		"6": "#E63B60",
# 		"7": "#8E5649",
# 		"8": "#68c99e",
# 		"9": "#a477c8",
# 		"10": "#5C76EC",
# 		"11": "#E773C3",
# 		"12": "#799fd2",
# 		"13": "#038a6c",
# 		"14": "#cc87fa",
# 		"15": "#ee8e76",
# 		"16": "#bbbbbb",
# 	}

    write_html(X, config)
    # Return config
    return config


def write_html(X, config, overwrite=True):
    """Write html.

    Parameters
    ----------
    X : data file

    Returns
    -------
    None.

    """
    content = {
        'json_data': X,
        'title': config['title'],
        'width': config['figsize'][0],
        'height': config['figsize'][1],
        'center': '"' + config['center'] + '"',
    }

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('movingbubbles.html.j2')
    index_file = Path(config['filepath'])
    print('Write to path: [%s]' % index_file.absolute())
    # index_file.write_text(index_template.render(content))
    if os.path.isfile(index_file):
        if overwrite:
            print('File already exists and will be overwritten: [%s]' %(index_file))
            os.remove(index_file)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


def import_example(filepath):
    print('Reading %s' %(filepath))
    lines = []
    with open(filepath) as f:
        for line in tqdm(f):
            # Remove patterns
            line = re.sub('[\n]', '', line)
            # Replace multiple spaces with a single one
            line = re.sub(' +', ' ', line)
            # Strip
            line = line.strip()
            lines.append(line)
    return lines
