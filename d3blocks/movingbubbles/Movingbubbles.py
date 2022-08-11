"""Moving bubble graph."""

import numpy as np
import pandas as pd
import datetime as dt
import re
from tqdm import tqdm
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os


def compute_time_delta(df, sample_id, datetime, state, cmap='Set1', dt_format='%Y-%m-%d %H:%M:%S'):
    """Compute delta between two time-points that follow-up.

    Parameters
    ----------
    df : Input DataFrame
        Input data.
    sample_id : str.
        Column name of the sample identifier.
    datetime : datetime
        Column name of the date time.
    state : str
        Column name that describes the state.
    cmap : str, (default: 'Set1')
        The name of the colormap.
        'Set1'.
    dt_format : str
        '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df : pd.DataFrame()
        DataFrame.

    """
    print('Compute time delta.')
    # Compute delta
    df = compute_delta(df, sample_id, datetime, dt_format=dt_format)
    # Return
    return df


def compute_delta(df, sample_id, datetime, dt_format='%Y-%m-%d %H:%M:%S'):
    """Compute date time delta.

    Description
    -----------
    The input for movingbubbles is the difference between two time points.
    The following steps are taken to compute the delta:
        1. Take event from an unique sample id
        2. Sort on datetime
        3. Compute stepwise the difference (delta) between two adjacent time points.

    Parameters
    ----------
    df : Input dataFrame
        Input data.
    sample_id : list of str.
        Category name.
    datetime : datetime
        date time.
    dt_format : str
        '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df : pd.DataFrame()
        One extra column is added that contains the time delta.

    """
    # Use copy of dataframe
    df = df.copy()
    df[sample_id] = df[sample_id].astype(str)
    # Check datetime format
    if not isinstance(df[datetime][0], dt.date):
        print('Set datetime format to [%s]' %(dt_format))
        df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

    # Initialize empty delta
    df['delta'] = df[datetime] - df[datetime]
    # Sort datetime
    df = df.sort_values(by=[sample_id, datetime])
    df.reset_index(inplace=True, drop=True)
    # Compute per category the delta
    for i in tqdm(np.unique(df[sample_id])):
        # Take sample id
        Iloc = df[sample_id]==i
        # Get data
        dftmp = df.loc[Iloc, :]
        # Store
        df.loc[np.where(Iloc)[0][:-1], 'delta'] = dftmp[datetime].iloc[1:].values - dftmp[datetime].iloc[:-1]

    # Set the last event at 0
    Iloc = df['delta'].isna()
    if np.any(Iloc):
        df.loc[np.where(Iloc)[0][:-1], 'delta'] = dftmp[datetime].iloc[0] - dftmp[datetime].iloc[0]
    # Return
    return df


def show(df, config, labels=None):
    """Build and show the graph.

    df : pd.DataFrame()
        Input dataframe.
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
    if not np.any(df.columns=='delta'):
        raise Exception('Column "delta" is missing in dataFrame of type datetime.')
    if config['center'] is None:
        # config['center'] = [*labels.keys()][0]
        config['center'] = ""
    # Extract minutes and days
    if config['reset_time']=='day':
        # df['time_in_state'] = (np.ceil(df['delta'].dt.seconds / 60)).astype(int)
        df['time_in_state'] = df['delta'].dt.seconds.astype(int)
    elif config['reset_time']=='year':
        df['time_in_state'] = df['delta'].dt.days.astype(int)

    # Transform dataframe into input form for d3
    X = []
    sid = np.array(list(map(lambda x: labels.get(x)['id'], df[config['columns']['state']].values)))
    uiid = np.unique(df['sample_id'])
    for i in uiid:
        Iloc=df['sample_id']==i
        tmplist=str(list(zip(sid[Iloc], df['time_in_state'].loc[Iloc].values)))
        tmplist=tmplist.replace('(', '')
        tmplist=tmplist.replace(')', '')
        tmplist=tmplist.replace('[', '')
        tmplist=tmplist.replace(']', '')
        tmplist=tmplist.replace(' ', '')
        # Make one big happy list
        X = [tmplist] + X

    # Set color codes for the d3js
    df_labels = pd.DataFrame(labels).T
    config['colorByActivity'] = dict(df_labels[['id', 'color']].values.astype(str))

    # Create the description for the numerical codes
    act_codes = []
    for label in labels:
        act_codes.append({"index": str(labels.get(label)['id']), "short": str(labels.get(label)['short']), "desc": str(labels.get(label)['desc'])})
    config['act_codes'] = act_codes

    # Used for percentages by minute
    act_counts = dict(zip(df_labels['id'].astype(str), np.zeros(len(df_labels['id'])).astype(int)))
    config['act_counts'] = act_counts

    # Define the starting day, hour, minute
    config['start_hour'] = df[config['columns']['datetime']].dt.hour[0]
    config['start_minute'] = df[config['columns']['datetime']].dt.minute[0]
    config['start_day'] = df[config['columns']['datetime']].dt.day[0]

    datestart = df[config['columns']['datetime']].iloc[0]
    datestop = df[config['columns']['datetime']].iloc[-1]
    config['note'] = config['note'] + "\nDate start: " + str(datestart) + "\n" + "Date stop:  " + str(datestop) + "\nRuntime: " + str(datestop - datestart) + "\nEstimated time to Finish: " + str(datestart + (datestop - datestart))

    # Write to HTML
    write_html(X, config)
    # Return config
    return config


def write_html(X, config, overwrite=True):
    """Write html.

    Parameters
    ----------
    X : list of str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.
    overwrite : bool (default: True)
        True: Overwrite current exiting html file.
        False: Do not overwrite existing html file.

    Returns
    -------
    None.

    """
    zero_to_hour = "0" if config['start_hour']<10 else ""
    zero_to_min = "0" if config['start_minute']<10 else ""

    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'CENTER': '"' + config['center'] + '"',
        'FONTSIZE': str(config['fontsize']) + 'px',
        'COLORBYACTIVITY': config['colorByActivity'],
        'ACT_CODES': config['act_codes'],
        'ACT_COUNTS': config['act_counts'],
        'SPEED': config['speed'],
        'DAMPER': config['damper'],
        'NOTE': config['note'],
        'START_HOUR_MIN': config['start_hour'] + (config['start_minute'] / 60),
        'START_TIME': zero_to_hour + str(config['start_hour']) + ":" + zero_to_min + str(config['start_minute']),
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


def standardize(df, sample_id='sample_id', datetime='datetime', dt_format='%Y-%m-%d %H:%M:%S'):
    """Standardize time per sample_id.

    Parameters
    ----------
    df : Input DataFrame
        Input data.
    sample_id : str.
        Column name of the sample identifier.
    datetime : datetime
        Column name of the date time.
    dt_format : str, optional
        '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df : DataFrame
        Dataframe with the input columns with an extra column with normalized time.
        'datetime_norm'

    """
    # Use copy of dataframe
    df = df.copy()
    # Get unique
    uis = df[sample_id].unique()
    df.reset_index(drop=True, inplace=True)

    # Check datetime format
    if not isinstance(df[datetime][0], dt.date):
        print('Set datetime format to [%s]' %(dt_format))
        df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

    # Add column with normalized time
    df['datetime_norm'] = df[datetime] - df[datetime]
    # Set a default start point.
    timenow = dt.datetime.strptime('1980-01-01 00:00:00', dt_format)

    # Normalize per unique sample id.
    for s in tqdm(uis):
        # Get data for specific sample-id
        idx = df[sample_id]==s
        dfs = df.loc[idx, :]
        # Normalize time per unique sample. Each sample will start at timenow.
        df.loc[idx, 'datetime_norm'] = timenow + (dfs[datetime].loc[idx] - dfs[datetime].loc[idx].min())

    # Set datetime
    df['datetime_norm'] = pd.to_datetime(df['datetime_norm'], format=dt_format, errors='ignore')
    # Return
    return df


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
