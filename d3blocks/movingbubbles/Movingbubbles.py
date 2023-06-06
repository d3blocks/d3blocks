"""Movingbubbles block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
Mail        : erdogant@gmail.com, oliver@sensibly.nl
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3

"""
import colourmap
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
try:
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, write_html_file
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration settings."""
    logger = kwargs.get('logger', None)
    config['chart'] ='movingbubbles'
    config['title'] = kwargs.get('title', 'Movingbubbles - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'movingbubbles.html'), logger)
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['figsize'] = kwargs.get('figsize', [780, 800])
    config['datetime'] = kwargs.get('datetime', 'datetime')
    config['sample_id'] = kwargs.get('sample_id', 'sample_id')
    config['state'] = kwargs.get('state', 'state')
    config['center'] = kwargs.get('center', None)
    config['damper'] = kwargs.get('damper', 1)
    config['fontsize'] = kwargs.get('fontsize', 14)
    config['timedelta'] = kwargs.get('timedelta', 'minutes')
    config['standardize'] = kwargs.get('standardize', None)
    config['speed'] = kwargs.get('speed', {"slow": 1000, "medium": 200, "fast": 50})
    config['note'] = kwargs.get('note', None)
    config['time_notes'] = kwargs.get('time_notes', None)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['dt_format'] = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    config['columns'] = kwargs.get('columns', {'datetime': config['datetime'], 'sample_id': config['sample_id'], 'state': config['state']})
    config['notebook'] = kwargs.get('notebook', False)
    config['color_method'] = kwargs.get('color_method', "STATE")

    return config


# %% Labels
def set_labels(labels, logger=None):
    """Set unique labels."""
    if isinstance(labels, pd.DataFrame):
        labels = labels.values.flatten()

    # Checks
    if (labels is None) or len(labels)<1:
        raise Exception(logger.error('Could not extract the labels!'))

    # Get unique categories without sort
    indexes = np.unique(labels, return_index=True)[1]
    uilabels = [labels[index] for index in sorted(indexes)]

    # Preprocessing
    # uilabels = pre_processing(uilabels)

    # Return
    return uilabels


# %% Node properties
def set_node_properties(labels, **kwargs):
    """Set the node properties for the Movingbubbles block.
    Parameters
    ----------
    labels : array-like or list.
        Contains the state names.
    center : String, (default: None)
        Center this category.
    cmap : String, (default: 'Set1')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv','inferno'

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    center = kwargs.get('center', None)
    cmap = kwargs.get('cmap', 'Set1')
    logger = kwargs.get('logger', None)

    # Set the unique labels
    uilabels = set_labels(labels)

    # Center should be at the very end of the list for d3!
    if center is not None:
        center_label = uilabels.pop(uilabels.index(center))
        if logger is not None: logger.info('Set the center state at: [%s]' %(center))
        uilabels.append(center_label)

    # Create unique label/node colors
    colors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex', verbose=0)

    # Make dict
    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i, 'label': label, 'short': label, 'desc': label, 'color': colors[i]}

    # Return
    return dict_labels


# %% Set Edge properties
def set_edge_properties(df, **kwargs):
    """Set the edge properties for the Movingbubbles block.

    Parameters
    ----------
    df : Input data, pd.DataFrame()
        Input data.
    size: dict. {'sample_id': size}
        Specify the sample_id as key with a node size. The default node size is set to 4.
            * size = {0: 10, 5: 20}
    datetime : str, (default: 'datetime')
        Name of the column with the datetime.
    sample_id : str, (default: 'sample_id')
        Name of the column with the sample ids.
    state : str, (default: 'state')
        Name of the column with the states.
    method : str. (default: None)
        Method to standardize the data.
        None: standardize over the entire timeframe. Sample_ids are dependent to each other.
        'samplewise': Standardize per sample_id. Thus the sample_ids are independent of each other.
    dt_format : str
        '%d-%m-%Y %H:%M:%S'.

    Returns
    -------
    df : pd.DataFrame()
        Processed dataframe.

    """
    datetime = kwargs.get('datetime', 'datetime')
    sample_id = kwargs.get('sample_id', 'sample_id')
    state = kwargs.get('state', 'state')
    method = kwargs.get('standardize', None)
    timedelta = kwargs.get('timedelta', None)
    size = kwargs.get('size', 4)
    color = kwargs.get('color', None)
    cmap = kwargs.get('cmap', 'Set1')
    dt_format = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    logger = kwargs.get('logger', None)
    df = df.copy()

    # Compute delta
    if ~np.any(df.columns=='delta') and isinstance(df, pd.DataFrame) and np.any(df.columns==state) and np.any(df.columns==datetime) and np.any(df.columns==sample_id):
        if logger is not None: logger.info('Standardizing input dataframe using method: [%s].' %(method))
        # df = self.compute_time_delta(df, sample_id=sample_id, datetime=datetime, dt_format=self.config['dt_format'])
        df = standardize(df, method=method, sample_id=sample_id, datetime=datetime, dt_format=dt_format, minimum_time=timedelta, logger=logger)
    else:
        raise Exception(print('Can not find the specified columns: "state", "datetime", or "sample_id" columns in the input dataframe: %s' %(df.columns.values)))

    # Set size per node. Note that sizes are still constant per node!
    df = _set_nodesize(df, sample_id, size, logger)
    # Colol per node
    df = _set_nodecolor(df, sample_id, color, cmap, logger)
    return df

def _set_nodecolor(df, sample_id, color, cmap, logger):
    # Node color is set to default.
    if isinstance(color, dict):
        # add new column to df with node color for the specified sample_id
        if logger is not None: logger.info('Processing the specified in node colors in dictionary..')
        df['color'] = '#808080'
        for key in color.keys():
            df.loc[df[sample_id]==key, 'color'] = color.get(key)

    if color is None:
        df['color'] = colourmap.fromlist(df['sample_id'], cmap=cmap, scheme='hex')[0]

    # If the color column not exists, create one with default color
    if not np.any(np.isin(df.columns, 'color')):
        df['color'] = color
        if logger is not None: logger.info('Set all nodes to color: %s' %(color))

    return df


def _set_nodesize(df, sample_id, size, logger):
    # Node size is set to default.
    if isinstance(size, dict):
        # add new column to df with node size for the specified sample_id
        if logger is not None: logger.info('Processing the specified in node sizes in dictionary..')
        df['size'] = 4
        for key in size.keys():
            df.loc[df[sample_id]==key, 'size'] = size.get(key)

    # If the size column not exists, create one with default size
    if not np.any(np.isin(df.columns, 'size')):
        df['size'] = size
        if logger is not None: logger.info('Set all nodes to size: %d' %(size))

    return df


def show(df, **kwargs):
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
    labels = kwargs.get('node_properties')
    logger = kwargs.get('logger', None)
    config = update_config(kwargs, logger)

    # Convert dict/frame.
    labels = convert_dataframe_dict(labels, frame=False)
    # df = convert_dataframe_dict(df, frame=True)

    if not np.any(df.columns=='delta'):
        raise Exception('Column "delta" is missing in dataFrame of type datetime.')
    if config['center'] is None:
        # config['center'] = [*labels.keys()][0]
        config['center'] = ""

    # Extract minutes and days
    if config['timedelta']=='seconds':
        df['time_in_state'] = df['delta'].dt.seconds.astype(int)
    elif config['timedelta']=='minutes':
        df['time_in_state'] = (np.ceil(df['delta'].dt.seconds / 60)).astype(int)
    elif config['timedelta']=='days':
        df['time_in_state'] = df['delta'].dt.days.astype(int)

    # Transform dataframe into input form for d3
    X = []
    sid = np.array(list(map(lambda x: labels.get(x)['id'], df[config['columns']['state']].values)))
    uiid = np.unique(df['sample_id'])
    for i in uiid:
        # Combine the sample_id with its time in state
        Iloc=df['sample_id']==i
        tmplist=str(list(zip(sid[Iloc], df['time_in_state'].loc[Iloc].values)))
        tmplist=tmplist.replace('(', '')
        tmplist=tmplist.replace(')', '')
        tmplist=tmplist.replace('[', '')
        tmplist=tmplist.replace(']', '')
        tmplist=tmplist.replace(' ', '')
        # Make one big happy list
        X = [tmplist] + X

    # Node size in the same order as the uiid
    nodedict = dict(zip(df['sample_id'], df['size']))
    config['node_size'] = list(map(lambda x: nodedict.get(x), uiid))

    # Node color in the same order as the uiid
    nodedict = dict(zip(df['sample_id'], df['color']))
    config['node_color'] = list(map(lambda x: nodedict.get(x), uiid))

    # Set color codes for the d3js
    df_labels = pd.DataFrame(labels).T
    config['colorByActivity'] = dict(df_labels[['id', 'color']].values.astype(str))
    # config['node_size'] = dict(zip(df_labels['id'].astype(str), df_labels['size']))
    # config['node_size'] = dict(zip(df['sample_id'], [4]*df.shape[0]))

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
    
    if config['note'] is None:
        config['note'] = "This is a simulation of multiple states and samples. <a href='https://github.com/d3blocks/d3blocks'>d3blocks movingbubbles</a>."
        config['note'] = config['note'] + "\nDate start: " + str(datestart) + "\n" + "Date stop:  " + str(datestop) + "\nRuntime: " + str(datestop - datestart) + "\nEstimated time to Finish: " + str(datestart + (datestop - datestart))

    if config['time_notes'] is None:
        config['time_notes'] = [{"start_minute": 1, "stop_minute": 2, "note": ""}]
    # Convert to json format
    config['time_notes'] = json.dumps(config['time_notes'])

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
    overwrite : bool (default: True)
        True: Overwrite current exiting html file.
        False: Do not overwrite existing html file.

    Returns
    -------
    None.

    """
    zero_to_hour = "0" if config['start_hour']<10 else ""
    zero_to_min = "0" if config['start_minute']<10 else ""

    # Set the selectionbox correctly on the form
    config['color_method'] = config['color_method'].upper()
    SELECTED_STATE = {'STATE': '', 'NODE': ''}
    SELECTED_STATE[config['color_method']] = 'selected="selected"'

    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'CENTER': '"' + config['center'] + '"',
        'FONTSIZE': str(config['fontsize']) + 'px',
        'COLORBYACTIVITY': config['colorByActivity'],

        'NODE_SIZE': config['node_size'],
        'NODE_COLOR': config['node_color'],
        'COLOR_STATE_SELECTED': SELECTED_STATE['STATE'],
        'COLOR_NODE_SELECTED': SELECTED_STATE['NODE'],

        'ACT_CODES': config['act_codes'],
        'ACT_COUNTS': config['act_counts'],
        'SPEED': config['speed'],
        'DAMPER': config['damper'],
        'NOTE': config['note'],
        'TIME_NOTES': config['time_notes'],
        'COLOR_METHOD': config['color_method'],
        'START_HOUR_MIN': config['start_hour'] + (config['start_minute'] / 60),
        'START_TIME': zero_to_hour + str(config['start_hour']) + ":" + zero_to_min + str(config['start_minute']),

        'SUPPORT': config['support'],

    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.movingbubbles', package_path='d3js'))

    index_template = jinja_env.get_template('movingbubbles.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


def standardize(df, method=None, sample_id='sample_id', datetime='datetime', dt_format='%d-%m-%Y %H:%M:%S', minimum_time='minutes', logger=None):
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
        '%d-%m-%Y %H:%M:%S'.

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
    if not isinstance(df[datetime].iloc[0], dt.date):
        if logger is not None: logger.info('Set datetime format to [%s]' %(dt_format))
        df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

    # Initialize empty delta
    df['delta'] = df[datetime] - df[datetime]
    # Initialize empty datetime_norm
    # df['datetime_norm'] = df[datetime] - df[datetime]
    # Set a default start point.
    # timenow = dt.datetime.strptime(dt.datetime.now().strftime(dt_format), dt_format)
    # timenow = timenow.replace(year=1980, month=1, day=1, hour=0, minute=0, second=0)

    if method=='samplewise':
        if logger is not None: logger.info('Standardize method: [%s]' %(method))
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
            # df.loc[Iloc, 'datetime_norm'] = timenow + (dfs[datetime].loc[Iloc] - dfs[datetime].loc[Iloc].min())
    elif method=='relative':
        df = df.sort_values(by=[datetime])
        df.reset_index(drop=True, inplace=True)

        # Note: The first state per sample_id is depended on the prevous state.
        # timedelta = df[datetime]-df[datetime]
        tmpdelta = df[datetime].iloc[1:].values - df[datetime].iloc[:-1]
        # timedelta.loc[1:] = tmpdelta.values
        df['delta'] = tmpdelta
        # tmpdelta = df[datetime].iloc[1:].values - df[datetime].iloc[:-1]
        # timedelta.loc[1:] = tmpdelta.values
        # df['delta'] = timedelta

        # Note: Last state per sample_id should always be ending and thus 0
        uisample_id = df['sample_id'].unique()
        getidx = []
        for sid in uisample_id:
            getidx.append(df[[sample_id, datetime]].loc[df[sample_id]==sid].sort_values(by=[datetime]).index[-1])
        df.loc[getidx, 'delta']=np.nan
        # df['datetime_norm'] = timenow + (df[datetime] - df[datetime].min())
    elif method=='minimum':
        df['delta'] = df['datetime'] - df['datetime'].min()


    # if NaT is found, set it to 0
    Iloc = df['delta'].isna()
    if np.any(Iloc):
        df.loc[Iloc, 'delta'] = df[datetime].iloc[0] - df[datetime].iloc[0]

    # Set datetime
    # df['datetime_norm'] = pd.to_datetime(df['datetime_norm'], format=dt_format, errors='ignore')
    # Sort on datetime
    df = df.sort_values(by=[datetime])
    df.reset_index(drop=True, inplace=True)

    # Zero time causes a total halt of movements. Prevent by adding a minimum time.
    zerotime=df['delta'][0] - df['delta'][0]
    Iloc = df['delta']==zerotime
    if np.any(Iloc):
        if minimum_time=='minutes':
            df.loc[Iloc, 'delta'] = df.loc[Iloc, 'delta'] + dt.timedelta(seconds=60)
        elif minimum_time=='days':
            df.loc[Iloc, 'delta'] = df.loc[Iloc, 'delta'] + dt.timedelta(days=1)
        else:
            df.loc[Iloc, 'delta'] = df.loc[Iloc, 'delta'] + dt.timedelta(seconds=1)

    # Return
    return df

def generate_data_with_random_datetime(n=10000, c=1000, date_start=None, date_stop=None, dt_format='%d-%m-%Y %H:%M:%S', logger=None):
    """Generate random time data.

    Parameters
    ----------
    n : int, (default: 10000).
        Number of events or data points.
    c : int, (default: 1000).
        Number of unique classes.
    date_start : str, (default: None)
        "17-12-1903 00:00:00" : start date
    date_stop : str, (default: None)
        "17-12-1913 23:59:59" : Stop date

    Returns
    -------
    df : DataFrame
        Example dataset with datetime.

    """
    if date_start is None:
        date_start="17-12-1903 00:00:00"
        logger.info('Date start is set to %s' %(date_start))
    if date_stop is None:
        date_stop="17-12-1913 23:59:59"
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


def random_date(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
    return str_time_prop(start, end, prop, dt_format=dt_format, strftime=strftime)


def str_time_prop(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
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
