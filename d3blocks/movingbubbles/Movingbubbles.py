"""Movingbubbles block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
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
    from .. utils import convert_dataframe_dict, set_path, pre_processing, update_config, write_html_file, include_save_to_svg_script, set_logo, resolve_color_background
except:
    from utils import convert_dataframe_dict, set_path, pre_processing, update_config, write_html_file, include_save_to_svg_script, set_logo, resolve_color_background


def _resolve_color_method(color_method, color_provided=False, logger=None):
    """Resolve color_method to one of {'STATE','NODE'}.

    AUTO resolves to NODE when user-supplied colors are provided, otherwise
    to STATE so state/activity colors remain the default behavior.
    """
    cm = str('AUTO' if color_method is None else color_method).upper()
    if cm == 'AUTO':
        resolved = 'NODE' if color_provided else 'STATE'
        if logger is not None:
            logger.info('[Movingbubbles] color_method="auto" resolved to [%s].' % (resolved.lower()))
        return resolved
    if cm not in {'STATE', 'NODE'}:
        if logger is not None:
            logger.warning('[Movingbubbles] Unknown color_method [%s]. Falling back to [state].' % (cm))
        return 'STATE'
    return cm


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration settings."""
    logger = kwargs.get('logger', None)
    config['chart'] ='movingbubbles'
    config['title'] = kwargs.get('title', 'Movingbubbles - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'movingbubbles.html'), logger)
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['figsize'] = kwargs.get('figsize', [1024, 768])
    config['datetime'] = kwargs.get('datetime', 'datetime')
    config['sample_id'] = kwargs.get('sample_id', 'sample_id')
    config['state'] = kwargs.get('state', 'state')
    config['center'] = kwargs.get('center', None)
    config['damper'] = kwargs.get('damper', 1)
    config['fontsize'] = kwargs.get('fontsize', 14)
    config['timedelta'] = kwargs.get('timedelta', 'minutes')
    config['standardize'] = kwargs.get('standardize', None)
    # Optional column name: when set, state durations are computed
    # independently within each group of that column (separate timelines).
    # None (default) = one shared timeline over the full dataframe.
    config['timelines'] = kwargs.get('timelines', None)
    config['speed'] = kwargs.get('speed', {"slow": 750, "medium": 250, "fast": 25, "superfast": 5})
    config['note'] = kwargs.get('note', None)
    config['time_notes'] = kwargs.get('time_notes', None)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['cmap'] = kwargs.get('cmap', 'Set1')
    config['dt_format'] = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    config['columns'] = kwargs.get('columns', {'datetime': config['datetime'], 'sample_id': config['sample_id'], 'state': config['state']})
    config['notebook'] = kwargs.get('notebook', False)
    config['color_provided'] = kwargs.get('color_provided', kwargs.get('color', None) is not None)
    config['color_method'] = _resolve_color_method(
        kwargs.get('color_method', 'AUTO'),
        color_provided=config['color_provided'],
        logger=logger,
    )
    config['save_button'] = kwargs.get('save_button', True)
    config['show_side_panel'] = kwargs.get('show_side_panel', True)
    config['show_top_panel'] = kwargs.get('show_top_panel', True)
    config['dark_mode'] = kwargs.get('dark_mode', True)
    # Prefer color_background; accept legacy background_color as single-hex fallback.
    if 'color_background' in kwargs:
        config['color_background'] = kwargs.get('color_background')
    elif 'background_color' in kwargs and kwargs.get('background_color') is not None:
        config['color_background'] = kwargs.get('background_color')
    else:
        config['color_background'] = None
    config['node_text_inside'] = kwargs.get('node_text_inside', True)
    config['opacity'] = kwargs.get('opacity', 0.6)
    config['stroke'] = kwargs.get('stroke', '#000000')

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
    timelines : str, optional (default: None)
        Column name (e.g. 'age', 'country'). When set, standardization runs
        independently inside each group of that column (separate timelines).
        None (default) = one shared timeline over the full dataframe.
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
    timelines = kwargs.get('timelines', None)
    timedelta = kwargs.get('timedelta', None)
    size = kwargs.get('size', 4)
    color = kwargs.get('color', None)
    opacity = kwargs.get('opacity', 0.6)
    stroke = kwargs.get('stroke', '#000000')
    config = kwargs.get('config', {})
    cmap = kwargs.get('cmap', config.get('cmap', 'Set1'))
    dt_format = kwargs.get('dt_format', '%d-%m-%Y %H:%M:%S')
    logger = kwargs.get('logger', None)
    df = df.copy()

    if not (isinstance(df, pd.DataFrame) and np.any(df.columns==state) and np.any(df.columns==datetime) and np.any(df.columns==sample_id)):
        raise Exception('Can not find the specified columns: "state", "datetime", or "sample_id" columns in the input dataframe: %s' %(df.columns.values))

    if timelines is not None:
        if not isinstance(timelines, str):
            raise Exception('[Movingbubbles] timelines must be a column name (str) or None, got %s.' % (type(timelines).__name__))
        if timelines not in df.columns:
            raise Exception(
                '[Movingbubbles] timelines column [%s] not found in the input dataframe. '
                'Available columns: %s' % (timelines, list(df.columns))
            )
        # Make sample_id unique within each timeline group.
        # When age (or country, …) cohort files are concatenated, the same uid
        # often appears in multiple groups. show() builds one schedule per
        # sample_id, so shared uids would merge states across groups and the
        # joint plot would look "averaged". Prefixing with the timeline value
        # gives each (timeline, sample) pair its own bubble — matching the
        # behavior of running each group subset separately.
        n_before = df[sample_id].nunique()
        df[sample_id] = (
            df[timelines].map(lambda x: 'NA' if pd.isna(x) else str(x))
            + '||'
            + df[sample_id].astype(str)
        )
        n_after = df[sample_id].nunique()
        if logger is not None and n_after != n_before:
            logger.info(
                'timelines=[%s]: expanded sample_id from %d to %d unique values '
                '(disambiguating ids that appear in multiple timeline groups).'
                % (timelines, n_before, n_after)
            )

    # Set size/color/opacity/stroke per node BEFORE standardize(): array-like
    # inputs are positionally aligned with the ORIGINAL row order (same
    # convention as scatter's set_edge_properties), and standardize() can
    # sort/reset the index depending on method -- attaching these as
    # dataframe columns first means that reordering carries the correct
    # value along with each row automatically instead of silently
    # misaligning a separately-tracked array.
    df = _set_nodesize(df, sample_id, size, logger)
    df = _set_nodecolor(df, sample_id, color, cmap, logger)
    df = _set_nodeopacity(df, sample_id, opacity, logger)
    df = _set_nodestroke(df, sample_id, stroke, logger)

    # Compute delta. When timelines is set, run standardization independently
    # inside each group of that column so events from other groups never affect
    # durations (fixes the "averaging out" effect on joint multi-group data).
    if logger is not None:
        if timelines is not None:
            logger.info('Standardizing input dataframe using method: [%s] with separate timelines per [%s].' % (method, timelines))
        else:
            logger.info('Standardizing input dataframe using method: [%s] (single timeline).' % (method))
    df = standardize(
        df,
        method=method,
        sample_id=sample_id,
        datetime=datetime,
        dt_format=dt_format,
        minimum_time=timedelta if timedelta else 'minutes',
        timelines=timelines,
        logger=logger,
    )

    return df


def _array_like_len_check(name, values, n):
    if len(values) != n:
        raise Exception('[Movingbubbles] Input parameter [%s] as an array/list/Series must have the same length as the input dataframe: expected %d, got %d.' % (name, n, len(values)))


def _is_hex_color(value):
    return isinstance(value, str) and bool(re.fullmatch(r'#[0-9a-fA-F]{6}', value))


def _labels_to_hex(labels, cmap):
    labels = pd.Series(labels, copy=False).astype(str).values
    colors = colourmap.fromlist(labels, cmap=cmap, scheme='hex', method='matplotlib', verbose=0)[0]
    return [str(c) for c in colors]


def _set_nodecolor(df, sample_id, color, cmap, logger):
    if isinstance(color, dict):
        # Per-node colors supplied as {sample_id: color}. Values can be hex
        # colors or categorical labels that are mapped via cmap.
        if logger is not None: logger.info('Processing the specified node colors as a dictionary..')
        df['color'] = '#808080'
        keys = list(color.keys())
        vals = list(color.values())
        if len(vals) > 0 and not np.all([_is_hex_color(v) for v in vals]):
            vals = _labels_to_hex(vals, cmap)
        for key, val in zip(keys, vals):
            df.loc[df[sample_id] == key, 'color'] = str(val)
    elif isinstance(color, (list, tuple, np.ndarray, pd.Series)):
        # Array-like, aligned positionally with the dataframe rows.
        color_arr = np.asarray(color)
        _array_like_len_check('color', color_arr, len(df))
        if np.all([_is_hex_color(v) for v in color_arr]):
            if logger is not None: logger.info('Processing the specified node colors as hex colors aligned with the dataframe..')
            df['color'] = [str(c) for c in color_arr]
        else:
            if logger is not None: logger.info('Processing the specified node colors as labels aligned with the dataframe and mapping via cmap..')
            df['color'] = _labels_to_hex(color_arr, cmap)
    elif color is None:
        # Derive colors from cmap based on sample_id
        df['color'] = _labels_to_hex(df[sample_id], cmap)
    else:
        # Single hex color string applied to all nodes
        df['color'] = str(color)
        if logger is not None: logger.info('Set all nodes to color: %s' %(color))
    
    return df


def _set_nodesize(df, sample_id, size, logger):
    if isinstance(size, dict):
        # add new column to df with node size for the specified sample_id
        if logger is not None: logger.info('Processing the specified node sizes as a dictionary..')
        df['size'] = 4
        for key in size.keys():
            df.loc[df[sample_id]==key, 'size'] = size.get(key)
    elif isinstance(size, (list, tuple, np.ndarray, pd.Series)):
        # Array-like, aligned positionally with the dataframe rows.
        size_arr = np.asarray(size)
        _array_like_len_check('size', size_arr, len(df))
        if logger is not None: logger.info('Processing the specified node sizes as an array aligned with the dataframe..')
        df['size'] = size_arr
    else:
        # Scalar: broadcast to all rows
        df['size'] = size
        if logger is not None: logger.info('Set all nodes to size: %s' %(str(size)))

    return df


def _set_nodeopacity(df, sample_id, opacity, logger):
    if isinstance(opacity, dict):
        if logger is not None: logger.info('Processing the specified node opacities as a dictionary..')
        df['opacity'] = 0.6
        for key in opacity.keys():
            df.loc[df[sample_id]==key, 'opacity'] = opacity.get(key)
    elif isinstance(opacity, (list, tuple, np.ndarray, pd.Series)):
        opacity_arr = np.asarray(opacity)
        _array_like_len_check('opacity', opacity_arr, len(df))
        if logger is not None: logger.info('Processing the specified node opacities as an array aligned with the dataframe..')
        df['opacity'] = opacity_arr
    else:
        df['opacity'] = opacity
        if logger is not None: logger.info('Set all nodes to opacity: %s' %(str(opacity)))

    return df


def _set_nodestroke(df, sample_id, stroke, logger):
    if isinstance(stroke, dict):
        if logger is not None: logger.info('Processing the specified node stroke colors as a dictionary..')
        df['stroke'] = '#000000'
        for key in stroke.keys():
            df.loc[df[sample_id]==key, 'stroke'] = str(stroke.get(key))
    elif isinstance(stroke, (list, tuple, np.ndarray, pd.Series)):
        stroke_arr = np.asarray(stroke)
        _array_like_len_check('stroke', stroke_arr, len(df))
        if logger is not None: logger.info('Processing the specified node stroke colors as an array aligned with the dataframe..')
        df['stroke'] = [str(c) for c in stroke_arr]
    else:
        df['stroke'] = str(stroke)
        if logger is not None: logger.info('Set all nodes to stroke: %s' %(stroke))

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
        df['time_in_state'] = df['delta'].dt.total_seconds().apply(lambda x: max(1, int(x))).astype(int)
    elif config['timedelta']=='minutes':
        df['time_in_state'] = df['delta'].dt.total_seconds().apply(lambda x: max(1, int(np.ceil(x / 60)))).astype(int)
    elif config['timedelta']=='days':
        df['time_in_state'] = df['delta'].dt.total_seconds().apply(lambda x: max(1, int(np.ceil(x / 86400)))).astype(int)

    # Transform dataframe into input form for d3
    X = []
    sid_col = config['columns']['sample_id']
    sid = np.array(list(map(lambda x: labels.get(x)['id'], df[config['columns']['state']].values)))
    uiid = np.unique(df[sid_col])
    # size/opacity schedules: one list per sample, aligned with that sample's
    # activity steps so the frontend can update radius/opacity on state change.
    node_size_sched = []
    node_opacity_sched = []
    for i in uiid:
        # Combine the sample_id with its time in state.
        # Take rows in datetime order so the schedule follows the true sequence
        # even if the frame was reordered.
        Iloc = (df[sid_col] == i).values
        order = np.argsort(df.loc[Iloc, config['columns']['datetime']].values, kind='mergesort')
        # Convert NumPy integers to regular Python integers to avoid np.int64 in string representation
        sid_values = [int(x) for x in np.asarray(sid)[Iloc][order]]
        time_values = [int(x) for x in df.loc[Iloc, 'time_in_state'].values[order]]
        tmplist=str(list(zip(sid_values, time_values)))
        tmplist=tmplist.replace('(', '')
        tmplist=tmplist.replace(')', '')
        tmplist=tmplist.replace('[', '')
        tmplist=tmplist.replace(']', '')
        tmplist=tmplist.replace(' ', '')
        # Make one big happy list
        X.append(tmplist)

        size_vals = df.loc[Iloc, 'size'].values[order]
        node_size_sched.append([
            int(v) if isinstance(v, (np.integer, int)) else float(v)
            for v in size_vals
        ])
        opacity_vals = df.loc[Iloc, 'opacity'].values[order]
        node_opacity_sched.append([float(v) for v in opacity_vals])

    # Per-sample size/opacity schedules (list of lists, same order as uiid /
    # schedule steps). Frontend uses index 0 at start and updates on each
    # activity transition so size/opacity track the current state.
    config['node_size'] = node_size_sched
    config['node_opacity'] = node_opacity_sched

    # Node color in the same order as the uiid
    nodedict = dict(zip(df[sid_col], df['color']))
    # Convert NumPy strings to regular Python strings for proper JSON serialization
    config['node_color'] = [str(nodedict.get(x)) if nodedict.get(x) is not None else nodedict.get(x) for x in uiid]

    # Node stroke color in the same order as the uiid
    nodedict = dict(zip(df[sid_col], df['stroke']))
    config['node_stroke'] = [str(nodedict.get(x)) if nodedict.get(x) is not None else nodedict.get(x) for x in uiid]

    # Set color codes for the d3js
    df_labels = pd.DataFrame(labels).T
    # Convert NumPy integers to regular Python integers and NumPy strings to regular Python strings for proper JSON serialization
    color_by_activity = {}
    for idx, row in df_labels[['id', 'color']].iterrows():
        color_by_activity[str(int(row['id']))] = str(row['color'])
    config['colorByActivity'] = color_by_activity
    # config['node_size'] = dict(zip(df_labels['id'].astype(str), df_labels['size']))
    # config['node_size'] = dict(zip(df['sample_id'], [4]*df.shape[0]))

    # Create the description for the numerical codes
    act_codes = []
    for label in labels:
        act_codes.append({
            "index": str(int(labels.get(label)['id'])), 
            "short": str(labels.get(label)['short']), 
            "desc": str(labels.get(label)['desc'])
        })
    config['act_codes'] = act_codes

    # Used for percentages by minute
    # Convert NumPy integers to regular Python strings for proper JSON serialization
    act_counts = {}
    for idx in df_labels['id']:
        act_counts[str(int(idx))] = 0
    config['act_counts'] = act_counts

    # Define the starting day, hour, minute
    config['start_hour'] = int(df[config['columns']['datetime']].dt.hour[0])
    config['start_minute'] = int(df[config['columns']['datetime']].dt.minute[0])
    config['start_day'] = int(df[config['columns']['datetime']].dt.day[0])

    datestart = df[config['columns']['datetime']].iloc[0]
    datestop = df[config['columns']['datetime']].iloc[-1]

    # Per-sample start date (first event date), in the same order as uiid.
    # Used by the frontend to power the dynamic date filter.
    first_dates = df.groupby(config['columns']['sample_id'])[config['columns']['datetime']].min()
    config['node_start_date'] = [first_dates.get(x).strftime('%Y-%m-%d') for x in uiid]

    # Overall date range covered by the data, used to bound the date filter control.
    config['date_min'] = df[config['columns']['datetime']].min().strftime('%Y-%m-%d')
    config['date_max'] = df[config['columns']['datetime']].max().strftime('%Y-%m-%d')

    # Per-sample property bags for the Layout panel (Size / Color / Shape / Label),
    # same role as scatter's d[13]. Every user-facing column is exposed:
    # sample_id, state, and any extra df columns. Internal/simulation columns
    # and columns generated by set_edge_properties (size, color) are reserved.
    # First non-null value per sample_id is kept.
    sid_col = config['columns']['sample_id']
    state_col = config['columns']['state']
    reserved_cols = {
        config['columns']['datetime'],
        'delta', 'time_in_state',
        'size',    # set by _set_nodesize, not an input variable
        'color',   # generated hex palette, not a data variable
        'opacity', # set by _set_nodeopacity, not an input variable
        'stroke',  # set by _set_nodestroke, not an input variable
    }
    prop_cols = [c for c in df.columns if c not in reserved_cols]
    # Guarantee sample_id and state are listed even if somehow missing from columns
    for required in (sid_col, state_col):
        if required not in prop_cols and required in df.columns:
            prop_cols.insert(0, required)

    def _jsonable(v):
        if v is None:
            return None
        try:
            if pd.isna(v):
                return None
        except Exception:
            pass
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, (np.bool_,)):
            return bool(v)
        if hasattr(v, 'item'):
            try:
                return v.item()
            except Exception:
                return str(v)
        if isinstance(v, (pd.Timestamp, dt.datetime, dt.date)):
            return str(v)
        return v if isinstance(v, (str, int, float, bool)) else str(v)

    node_props = []
    for sid in uiid:
        props = {}
        sub = df.loc[df[sid_col] == sid]
        for col in prop_cols:
            series = sub[col].dropna()
            if len(series) == 0:
                continue
            props[str(col)] = _jsonable(series.iloc[0])
        # Always present for labeling / coloring
        props[str(sid_col)] = _jsonable(sid)
        if str(state_col) not in props and state_col in sub.columns:
            series = sub[state_col].dropna()
            if len(series):
                props[str(state_col)] = _jsonable(series.iloc[0])
        node_props.append(props)
    config['node_props'] = node_props
    # Stable ordered key list so the Layout dropdowns show every variable
    # even when some samples lack a value for a given column.
    seen = []
    for col in prop_cols:
        name = str(col)
        if name not in seen:
            seen.append(name)
    for bag in node_props:
        for k in bag.keys():
            if k not in seen:
                seen.append(k)
    config['prop_keys'] = seen

    if config['note'] is None:
        config['note'] = "D3Blocks Movingubbles"
        # config['note'] = config['note'] + "\nDate start: " + str(datestart) + "\n" + "Date stop:  " + str(datestop) + "\nRuntime: " + str(datestop - datestart) + "\nEstimated time to Finish: " + str(datestart + (datestop - datestart))

    if config['time_notes'] is None:
        config['time_notes'] = [{"start_minute": 1, "stop_minute": 2, "note": ""}]
    # Convert to json format
    config['time_notes'] = json.dumps(config['time_notes'])

    # Set logo
    config['logo_base64'] = set_logo(filepath=config['logo'])

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
    # Save button
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])

    # Set time
    zero_to_hour = "0" if config['start_hour']<10 else ""
    zero_to_min = "0" if config['start_minute']<10 else ""

    # Set the selectionbox correctly on the form
    config['color_method'] = _resolve_color_method(
        config.get('color_method', 'AUTO'),
        color_provided=config.get('color_provided', False),
        logger=logger,
    )
    SELECTED_STATE = {'STATE': '', 'NODE': ''}
    SELECTED_STATE[config['color_method']] = 'selected="selected"'
    bg_dark, bg_light = resolve_color_background(config.get('color_background'))

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
        'NODE_PROPS': json.dumps(config.get('node_props', [])),
        'PROP_KEYS': json.dumps(config.get('prop_keys', [])),
        'STATE_COL': json.dumps(config['columns']['state']),
        'SAMPLE_ID_COL': json.dumps(config['columns']['sample_id']),
        'COLOR_STATE_SELECTED': SELECTED_STATE['STATE'],
        'COLOR_NODE_SELECTED': SELECTED_STATE['NODE'],

        'ACT_CODES': config['act_codes'],
        'ACT_COUNTS': config['act_counts'],
        'SPEED': config['speed'],
        'DAMPER': config['damper'],
        'NOTE': config['note'],
        'TIME_NOTES': config['time_notes'],
        'COLOR_METHOD': config['color_method'],
        'COLOR_PROVIDED': 'true' if config.get('color_provided', False) else 'false',
        'START_HOUR_MIN': config['start_hour'] + (config['start_minute'] / 60),
        'START_TIME': zero_to_hour + str(config['start_hour']) + ":" + zero_to_min + str(config['start_minute']),
        'TIMEDELTA': config['timedelta'],

        'NODE_START_DATE': config['node_start_date'],
        'DATE_MIN': config['date_min'],
        'DATE_MAX': config['date_max'],

        'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
        'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
        'darkMode': 'true' if config.get('dark_mode', True) else 'false',
        'COLOR_BACKGROUND_DARK': bg_dark,
        'COLOR_BACKGROUND_LIGHT': bg_light,
        'nodeTextInside': str(config.get('node_text_inside', True)).lower(),
        'NODE_OPACITY': config['node_opacity'],
        'NODE_STROKE': config['node_stroke'],

        'SUPPORT': config['support'],
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
        'LOGO_BASE64': config['logo_base64'],

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


def standardize(df, method=None, sample_id='sample_id', datetime='datetime', dt_format='%d-%m-%Y %H:%M:%S', minimum_time='minutes', timelines=None, logger=None):
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
    timelines : str or None, optional (default: None)
        When set to a column name (e.g. 'age', 'country'), the chosen
        standardize method is applied independently inside each group of
        that column (separate timelines). None = one shared timeline over
        the full dataframe. Events from other groups never contribute to
        a sample's state durations.

    Returns
    -------
    df : DataFrame
        Dataframe with the input columns with an extra column with standardized time.
        'datetime_norm'

    """
    # Use copy of dataframe
    df = df.copy()

    # Check datetime format once (before any grouping)
    if not isinstance(df[datetime].iloc[0], dt.date):
        if logger is not None: logger.info('Set datetime format to [%s]' %(dt_format))
        df[datetime] = pd.to_datetime(df[datetime], format=dt_format)

    # When a timelines column is given, run the chosen standardize method
    # independently inside each group. Events from other groups never enter
    # the delta calculation, so a joint multi-group dataframe behaves like
    # running the same method on each group subset separately.
    if timelines is not None:
        if timelines not in df.columns:
            raise Exception(
                '[Movingbubbles] timelines column [%s] not found in the input dataframe. '
                'Available columns: %s' % (timelines, list(df.columns))
            )
        n_groups = int(df[timelines].nunique(dropna=False))
        if logger is not None:
            logger.info(
                'Applying standardize method [%s] independently for %d timelines in column [%s].'
                % (method, n_groups, timelines)
            )
        parts = []
        for _tl_val, g in df.groupby(timelines, sort=False, dropna=False):
            g_std = standardize(
                g.copy(),
                method=method,
                sample_id=sample_id,
                datetime=datetime,
                dt_format=dt_format,
                minimum_time=minimum_time,
                timelines=None,
                logger=None,
            )
            parts.append(g_std)
        out = pd.concat(parts, axis=0, ignore_index=True)
        out = out.sort_values(by=[datetime])
        out.reset_index(drop=True, inplace=True)
        return out

    # Get unique sample ids
    uis = df[sample_id].unique()

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
        # Standardize per unique sample id: duration of each state is the
        # wall-clock gap until *this sample's* next event (never another sample).
        for s in tqdm(uis):
            idxs = df.index[df[sample_id] == s].tolist()
            if not idxs:
                continue
            # Gaps between consecutive events of this sample
            for a, b in zip(idxs[:-1], idxs[1:]):
                df.at[a, 'delta'] = df.at[b, datetime] - df.at[a, datetime]
            # Last event has no successor
            df.at[idxs[-1], 'delta'] = pd.NaT
    elif method is None:
        # Global mode: deltas are real wall-clock gaps between consecutive events
        # across all sample_ids in this frame, sorted by datetime.
        #
        # delta[i] = time[i+1] - time[i] for i = 0..n-2  (positional numpy assign).
        # Must write into rows 0..n-2, NOT 1..n-1 — the latter left row 0 stuck at
        # the zero initializer so every simulation started with a 1-minute first
        # state. A Series assign would also re-align on index and shift gaps.
        if logger is not None: logger.info('Standardize method: [global/None]')
        df = df.sort_values(by=[datetime])
        df.reset_index(drop=True, inplace=True)
        if len(df) >= 2:
            tmpdelta = df[datetime].iloc[1:].values - df[datetime].iloc[:-1].values
            df.loc[df.index[:-1], 'delta'] = tmpdelta
        # Last event of each sample has no successor in that sample's schedule
        for s in uis:
            sample_rows = df.index[df[sample_id] == s]
            if len(sample_rows):
                df.at[sample_rows[-1], 'delta'] = pd.NaT
    elif method=='relative':
        df = df.sort_values(by=[datetime])
        df.reset_index(drop=True, inplace=True)

        # Gaps between consecutive rows in global time order.
        # Write into rows 0..n-2 (same fix as global/None).
        if len(df) >= 2:
            tmpdelta = df[datetime].iloc[1:].values - df[datetime].iloc[:-1].values
            df.loc[df.index[:-1], 'delta'] = tmpdelta

        # Last state per sample_id should always be ending
        for sid in df[sample_id].unique():
            sample_rows = df.index[df[sample_id] == sid]
            if len(sample_rows):
                df.at[sample_rows[-1], 'delta'] = pd.NaT
    elif method=='minimum':
        df['delta'] = df[datetime] - df[datetime].min()


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
        if minimum_time=='seconds':
            df.loc[Iloc, 'delta'] = df.loc[Iloc, 'delta'] + dt.timedelta(seconds=1)
        elif minimum_time=='minutes':
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
    idx_middle=int(np.where(np.array(location_types)=='Travel')[0][0])
    i=0
    while i <= df.shape[0]-3:
    # for i in tqdm(range(0, df.shape[0])):
        # A specific sample always contains 3 states. The start-state, the travel-state and the end-state.

        # Get the particular sample-id
        sample_id = random.randint(0, c)
        state_prev = state_mem.get(sample_id, None)

        # Set the start state:
        # Get random idx based pdf
        df.loc[i, 'sample_id'] = sample_id
        idx = int(np.random.choice(np.arange(0, len(location_types)), p=pdf))
        if (state_prev is not None) and (idx==state_prev['state']):
            idx = int(np.mod(idx+1, len(location_types)))
        df.loc[i, 'state'] = location_types[idx]
        df.loc[i, 'datetime'] = random_date(date_start, date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # The travel-state:
        df.loc[i, 'sample_id'] = sample_id
        df.loc[i, 'state'] = location_types[idx_middle]
        df.loc[i, 'datetime'] = random_date(df['datetime'].iloc[i-1], date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # Set the end state:
        # Get random idx based pdf
        df.loc[i, 'sample_id'] = sample_id
        idx = int(np.random.choice(np.arange(0, len(location_types)), p=pdf))
        if (location_types[idx]==df['state'].iloc[i-1]):
            idx = int(np.mod(idx+1, len(location_types)))

        df.loc[i, 'state'] = location_types[idx]
        df.loc[i, 'datetime'] = random_date(df['datetime'].iloc[i-1], date_stop, random.random(), dt_format=dt_format)
        i = i + 1

        # Store the last state
        state_mem[sample_id] = {'state':int(idx)}

        # Rotate pdf list
        # pdf.insert(0, pdf.pop())

    # Set a random time-point at multiple occasion at the same time.
    # df['datetime'].iloc[np.array(list(map(lambda x: random.randint(0, c), np.arange(0, c/20))))] = df['datetime'].iloc[0]
    df['datetime'] = pd.to_datetime(df['datetime'], format=dt_format)
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