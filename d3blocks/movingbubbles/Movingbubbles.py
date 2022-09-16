"""Moving bubble graph."""

import numpy as np
import pandas as pd
import datetime as dt
import re
from tqdm import tqdm
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import json
import random
import time


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
    # Convert to json format
    config['time_notes'] = json.dumps(config['time_notes'])

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
        'TIME_NOTES': config['time_notes'],
        'START_HOUR_MIN': config['start_hour'] + (config['start_minute'] / 60),
        'START_TIME': zero_to_hour + str(config['start_hour']) + ":" + zero_to_min + str(config['start_minute']),
    }

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('movingbubbles.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


def standardize(df, method=None, sample_id='sample_id', datetime='datetime', dt_format='%Y-%m-%d %H:%M:%S'):
    """Standardize time per sample_id.

    Parameters
    ----------
    df : Input DataFrame
        Input data.
    method : str. (default: None)
        Method to standardize the data.
        None: standardize over the entire timeframe. Sample_ids are dependent to each other.
        'samplewise': standardize per sample_id. Thus the sample_ids are independent of each other.
    sample_id : str.
        Column name of the sample identifier.
    datetime : datetime
        Column name of the date time.
    dt_format : str, optional
        '%Y-%m-%d %H:%M:%S'.

    Returns
    -------
    df : DataFrame
        Dataframe with the input columns with an extra column with standardized time.
        'datetime_norm'

    """
    # Use copy of dataframe
    df = df.copy()
    # Get unique
    uis = df[sample_id].unique()

    # Check datetime format
    if not isinstance(df[datetime][0], dt.date):
        print('[D3Blocks]> Set datetime format to [%s]' %(dt_format))
        df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

    # Initialize empty delta
    df['delta'] = df[datetime] - df[datetime]
    # Initialize empty datetime_norm
    df['datetime_norm'] = df[datetime] - df[datetime]
    # Set a default start point.
    timenow = dt.datetime.strptime('1980-01-01 00:00:00', dt_format)

    if method=='samplewise':
        print('[D3Blocks]> Standardize method: [%s]' %(method))
        df = df.sort_values(by=[sample_id, datetime])
        df.reset_index(drop=True, inplace=True)
        # Standardize per unique sample id.
        for s in tqdm(uis):
            # Get data for specific sample-id
            Iloc = df[sample_id]==s
            dfs = df.loc[Iloc, :]
            # Timedelta
            timedelta = dfs[datetime].iloc[1:].values - dfs[datetime].iloc[:-1]
            df.loc[Iloc, 'delta'] = timedelta
            # Standardize time per unique sample. Each sample will start at timenow.
            df.loc[Iloc, 'datetime_norm'] = timenow + (dfs[datetime].loc[Iloc] - dfs[datetime].loc[Iloc].min())
    else:
        df = df.sort_values(by=[datetime])
        df.reset_index(drop=True, inplace=True)
        timedelta = df[datetime].iloc[1:].values - df[datetime].iloc[:-1]
        df['delta'] = timedelta
        df['datetime_norm'] = timenow + (df[datetime] - df[datetime].min())

    Iloc = df['delta'].isna()
    if np.any(Iloc):
        df.loc[Iloc, 'delta'] = df[datetime].iloc[0] - df[datetime].iloc[0]

    # Set datetime
    df['datetime_norm'] = pd.to_datetime(df['datetime_norm'], format=dt_format, errors='ignore')
    # Sort on datetime
    df = df.sort_values(by=[datetime])
    df.reset_index(drop=True, inplace=True)
    # Return
    return df


# def compute_time_delta(df, sample_id, datetime, dt_format='%Y-%m-%d %H:%M:%S'):
#     """Compute delta between two time-points that follow-up.

#     Parameters
#     ----------
#     df : Input DataFrame
#         Input data.
#     sample_id : str.
#         Column name of the sample identifier.
#     datetime : datetime
#         Column name of the date time.
#     dt_format : str
#         '%Y-%m-%d %H:%M:%S'.

#     Returns
#     -------
#     df : pd.DataFrame()
#         DataFrame.

#     """
#     print('Compute time delta.')
#     # Compute delta
#     df = compute_delta(df, sample_id, datetime, dt_format=dt_format)
#     # Return
#     return df


# def compute_time_delta(df, sample_id, datetime, dt_format='%Y-%m-%d %H:%M:%S'):
#     """Compute date time delta.

#     Description
#     -----------
#     The input for movingbubbles is the difference between two time points.
#     The following steps are taken to compute the delta:
#         1. Take event from an unique sample id
#         2. Sort on datetime
#         3. Compute sample-wise and stepwise the difference (delta) between two adjacent time points.

#     Parameters
#     ----------
#     df : Input dataFrame
#         Input data.
#     sample_id : list of str.
#         Category name.
#     datetime : datetime
#         date time.
#     dt_format : str
#         '%Y-%m-%d %H:%M:%S'.

#     Returns
#     -------
#     df : pd.DataFrame()
#         One extra column is added that contains the time delta.

#     """
#     # Use copy of dataframe
#     df = df.copy()
#     df[sample_id] = df[sample_id].astype(str)
#     # Check datetime format
#     if not isinstance(df[datetime][0], dt.date):
#         print('Set datetime format to [%s]' %(dt_format))
#         df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

#     # Initialize empty delta
#     df['delta'] = df[datetime] - df[datetime]
#     # Sort datetime
#     df = df.sort_values(by=[sample_id, datetime])
#     df.reset_index(inplace=True, drop=True)
#     # idx = None
#     # Compute sample-wise the time-delta
#     for i in tqdm(np.unique(df[sample_id])):
#         # Take sample id
#         Iloc = df[sample_id]==i
#         # Get data
#         dftmp = df.loc[Iloc, :]
#         # Take last time point from previous sample.
#         # df[datetime].iloc[idx] - df[datetime].iloc[idx+1]
#         # Store
#         df.loc[np.where(Iloc)[0][:-1], 'delta'] = dftmp[datetime].iloc[1:].values - dftmp[datetime].iloc[:-1]
#         # Store index
#         # idx = np.where(Iloc)[0].max()

#     # Set the last event at 0
#     Iloc = df['delta'].isna()
#     if np.any(Iloc):
#         df.loc[np.where(Iloc)[0][:-1], 'delta'] = dftmp[datetime].iloc[0] - dftmp[datetime].iloc[0]
#     # Return
#     return df

def generate_data_with_random_datetime(n=10000, c=1000, date_start=None, date_stop=None, dt_format='%Y-%m-%d %H:%M:%S', logger=None):
    """Generate random time data.

    Parameters
    ----------
    n : int, (default: 10000).
        Number of events or data points.
    c : int, (default: 1000).
        Number of unique classes.
    date_start : str, (default: None)
        "1-1-2000 00:00:00" : start date
    date_stop : str, (default: None)
        1-1-2010 23:59:59" : Stop date

    Returns
    -------
    df : DataFrame
        Example dataset with datetime.

    """
    if date_start is None:
        date_start="2000-01-01 00:00:00"
        logger.info('Date start is set to %s' %(date_start))
    if date_stop is None:
        date_stop="2010-01-01 23:59:59"
        logger.info('Date start is set to %s' %(date_stop))

    # Create empty dataframe
    df = pd.DataFrame(columns=['datetime', 'sample_id', 'state'], data=np.array([[None, None, None]] * n))
    location_types = ['Home', 'Hospital', 'Bed', 'Sport', 'Sleeping', 'Sick', 'Work', 'Eating', 'Bored']
    # Take random few columns
    # location_types = location_types[0:random.randint(2, len(location_types))]
    # Always add the column Travel
    location_types = location_types + ['Travel']
    # Set the probability of selecting a certain state
    pdf = [0.05, 0.02, 0.02, 0.1, 0.55, 0.05, 0.1, 0.03, 0.03, 0.05]

    # Generate random timestamps with catagories and sample ids
    state_mem = {}
    idx_middle=np.where(np.array(location_types)=='Travel')[0][0]
    i=0
    while i <= df.shape[0]-3:
    # for i in tqdm(range(0, df.shape[0])):
        # A specific sample always contains 3 states. The start-state, the travel-state and the end-state.

        # Get the particular sample-id
        sample_id = random.randint(0, c)
        state_prev = state_mem.get(sample_id, None)

        # Set the start state:
        # Get random idx based pdf
        df['sample_id'].iloc[i] = sample_id
        idx = np.random.choice(np.arange(0, len(location_types)), p=pdf)
        if (state_prev is not None) and (idx==state_prev['state']):
            idx = np.mod(idx+1, len(location_types))
        df['state'].iloc[i] = location_types[idx]
        df['datetime'].iloc[i] = random_date(date_start, date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # The travel-state:
        df['sample_id'].iloc[i] = sample_id
        df['state'].iloc[i] = location_types[idx_middle]
        df['datetime'].iloc[i] = random_date(df['datetime'].iloc[i-1], date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # Set the end state:
        # Get random idx based pdf
        df['sample_id'].iloc[i] = sample_id
        idx = np.random.choice(np.arange(0, len(location_types)), p=pdf)
        if (location_types[idx]==df['state'].iloc[i-1]):
            idx = np.mod(idx+1, len(location_types))

        df['state'].iloc[i] = location_types[idx]
        df['datetime'].iloc[i] = random_date(df['datetime'].iloc[i-1], date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # Store the last state
        state_mem[sample_id] = {'state':idx}
        
        # Rotate pdf list
        # pdf.insert(0, pdf.pop())

        
    # Set a random time-point at multiple occasion at the same time.
    # df['datetime'].iloc[np.array(list(map(lambda x: random.randint(0, c), np.arange(0, c/20))))] = df['datetime'].iloc[0]
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by="datetime")
    df.dropna(inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df


def random_date(start, end, prop, dt_format='%Y-%m-%d %H:%M:%S', strftime=True):
    return str_time_prop(start, end, prop, dt_format=dt_format, strftime=strftime)


def str_time_prop(start, end, prop, dt_format='%Y-%m-%d %H:%M:%S', strftime=True):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, dt_format))
    etime = time.mktime(time.strptime(end, dt_format))
    ptime = stime + prop * (etime - stime)
    if strftime:
        return time.strftime(dt_format, time.localtime(ptime))
    else:
        return time.localtime(ptime)


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
