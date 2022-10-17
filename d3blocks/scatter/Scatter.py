"""Scatter block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

# import colourmap

try:
    from .. utils import set_colors
except:
    from utils import set_colors
import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import pandas as pd
import time


# %% Preprocessing
def check_exceptions(x, y, x1, y1, x2, y2, s, c, tooltip, config, logger):
    """Check Exceptions."""
    # if len(config['label_radio'])!=sum(list(map(lambda x: x=='', config['radio_button_visible']))): raise Exception(logger.error('input parameter [label_radio] must contain the correct number of labels depending on the (x,y), (x1,y1), (x2,y2) coordinates.'))
    if len(x)!=len(y): raise Exception(logger.error('input parameter [x] and [y] should be of size of (x, y).'))
    if s is None: raise Exception(logger.error('input parameter [s] should have value >0.'))
    if c is None: raise Exception(logger.error('input parameter [c] should be of a list of string with hex color, such as "#000000".'))
    if isinstance(s, (list, np.ndarray)) and (len(s)!=len(x)): raise Exception(logger.error('input parameter [s] should be of same size of (x, y).'))
    if (tooltip is not None) and len(tooltip)!=len(x): raise Exception(logger.error('input parameter [tooltip] should be of size (x, y) and not None.'))

    if (x1 is not None) or (y1 is not None):
        if len(x1)!=len(y1): raise Exception(logger.error('input parameter [x1] should be of size of (x1, y1).'))
        if len(x)!=len(x1): raise Exception(logger.error('input parameter (x1, y1) should be of size of (x, y).'))
    if (x2 is not None) or (y2 is not None):
        if len(x2)!=len(y2): raise Exception(logger.error('input parameter [x2] should be of size of (x2, y2).'))
        if len(x)!=len(x2): raise Exception(logger.error('input parameter (x2, y2) should be of size of (x, y).'))


# %% Preprocessing
def preprocessing(x, y, x1, y1, x2, y2, color='#69b3a2', size=5, tooltip=None, opacity=0.8, c_gradient=None, stroke='#ffffff', cmap='Set2', scale=False, logger=None):
    """Preprocessing."""
    if (x1 is None): x1 = x
    if (y1 is None): y1 = y
    if (x2 is None): x2 = x
    if (y2 is None): y2 = y

    # Combine into array
    X = np.c_[x, y]
    # Combine second coordinates into array
    X1 = np.c_[x1, y1]
    X2 = np.c_[x2, y2]

    # Scale data
    if scale:
        logger.info('Scaling xy-coordinates.')
        X = _scale_xy(X)
        X1 = _scale_xy(X1)
        X2 = _scale_xy(X2)
    # In case only one (s)ize is defined. Set all points to this size.
    if isinstance(size, (int, float)): size = np.repeat(size, X.shape[0])
    if np.any(size<0):
        logger.info('[%.0d] sizes are <0 and set to 0.' %(np.sum(size<0)))
        size[size<0]=0
    # In case None tooltip is defined. Set all points to this tooltip.
    if tooltip is None: tooltip = np.repeat('', X.shape[0])
    # In case only one opacity is defined. Set all points to this size.
    if isinstance(opacity, (int, float)): opacity = np.repeat(opacity, X.shape[0])
    # colors
    c, labels = set_colors(X, color, cmap, c_gradient=c_gradient)
    # In case stroke is None: use same colors as for c.
    if stroke is None:
        stroke = c
    elif isinstance(stroke, str):
        # In case only one stroke is defined. Set all points to this size.
        stroke = np.repeat(stroke, X.shape[0])

    # Make dict with properties
    dict_properties = {}
    for i in range(0, X.shape[0]):
        dict_properties[i] = {'id': labels[i], 'x': X[i][0], 'y': X[i][1], 'x1': X1[i][0], 'y1': X1[i][1], 'x2': X2[i][0], 'y2': X2[i][1], 'color': color[i], 'dotsize': size[i], 'stroke': stroke[i], 'opacity': opacity[i], 'desc': tooltip[i], 'short': labels[i]}

    # Create the plot
    df = pd.DataFrame(dict_properties).T

    # return
    return df, dict_properties


# %% Scale data
def _scale_xy(X):
    """Scale xy coordinates."""
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    return (X - x_min) / (x_max - x_min)


# %% Setup colors
# def set_colors(X, c, cmap, c_gradient=None):
#     """Scatterplots."""
#     hexok = False
#     # In case only one (c)olor is defined. Set all to this value.
#     if isinstance(c, str): c = np.repeat(c, X.shape[0])

#     # Check whether the input is hex colors.
#     hexok = np.all(list(map(lambda x: (x[0]=='#') and (len(x)==7), c)))

#     if hexok:
#         # Input is hex-colors thus we do not need to touch the colors.
#         labels = np.arange(0, X.shape[0]).astype(str)
#         c_hex = c
#     else:
#         # The input are string-labels and not colors. Lets convert to hex-colors.
#         labels = c
#         c_hex, _ = colourmap.fromlist(c, cmap=cmap, method='matplotlib', gradient=c_gradient, scheme='hex')

#     if (c_gradient is not None):
#         c_hex = _density_color(X, c_hex, c)

#     # Return
#     return c_hex, labels


# %% Create gradient based based on the labels.
# def _density_color(X, colors, labels):
#     """Scatterplots."""
#     from scipy.stats import gaussian_kde
#     uilabels = np.unique(labels)
#     density_colors = np.repeat('#ffffff', X.shape[0])

#     if (len(uilabels)!=len(labels)):
#         for label in uilabels:
#             idx = np.where(labels==label)[0]
#             if X.shape[1]==2:
#                 xy = np.vstack([X[idx, 0], X[idx, 1]])
#             else:
#                 xy = np.vstack([X[idx, 0], X[idx, 1], X[idx, 2]])

#             try:
#                 # Compute density
#                 z = gaussian_kde(xy)(xy)
#                 # Sort on density
#                 didx = idx[np.argsort(z)[::-1]]
#             except:
#                 didx=idx

#             # order colors correctly based Density
#             density_colors[didx] = colors[idx]
#             # plt.figure()
#             # plt.scatter(X[didx,0], X[didx,1], color=colors[idx, :])
#             # plt.figure()
#             # plt.scatter(idx, idx, color=colors[idx, :])
#         colors = density_colors

#     # Return
#     return colors


# %% Show
def show(df, config):
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
    # Compute xlim and ylim for the axis.
    spacing = 0.12
    if config['xlim']==[None, None] or len(config['xlim'])==0:
        maxvalue = df[['x', 'x1', 'x2']].max().max()
        minvalue = df[['x', 'x1', 'x2']].min().min()
        x_spacing = ((maxvalue - minvalue) * spacing)
        config['xlim'] = [minvalue - x_spacing, maxvalue + x_spacing]
        # x_spacing = (df['x'].max() - df['x'].min()) * spacing
        # config['xlim'] = [df['x'].min() - x_spacing, df['x'].max() + x_spacing]
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        maxvalue = df[['y', 'y1', 'y2']].max().max()
        minvalue = df[['y', 'y1', 'y2']].min().min()
        y_spacing = ((maxvalue - minvalue) * spacing)
        config['ylim'] = [minvalue - y_spacing, maxvalue + y_spacing]
        # y_spacing = (df['y'].max() - df['y'].min()) * spacing
        # config['ylim'] = [df['y'].min() - y_spacing, df['y'].max() + y_spacing]

    # Create the data from the input of javascript
    X = get_data_ready_for_d3(df)
    # Check whether tooltip is available. Otherwise remove the tooltip box.
    if np.all(df['desc']==''):
        config['mouseover'] = ''
        config['mousemove'] = ''
        config['mouseleave'] = ''
    else:
        config['mouseover'] = '.on("mouseover", mouseover)'
        config['mousemove'] = '.on("mousemove", mousemove)'
        config['mouseleave'] = '.on("mouseleave", mouseleave)'

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
        'MIN_X': config['xlim'][0],
        'MAX_X': config['xlim'][1],
        'MIN_Y': config['ylim'][0],
        'MAX_Y': config['ylim'][1],
        'RADIO_LABEL1': config['label_radio'][0],
        'RADIO_LABEL2': config['label_radio'][1],
        'RADIO_LABEL3': config['label_radio'][2],
        'RADIO_VISIBLE1': config['radio_button_visible'][0],
        'RADIO_VISIBLE2': config['radio_button_visible'][1],
        'RADIO_VISIBLE3': config['radio_button_visible'][2],
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'],
        'MOUSELEAVE': config['mouseleave'],
    }

    # print('NAME')
    # print(__name__)
    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.scatter', package_path='d3js'))

    index_template = jinja_env.get_template('scatter.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


def get_data_ready_for_d3(df):
    """Convert the source-target data into d3 compatible data.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.

    Returns
    -------
    X : str.
        Converted data into a string that is d3 compatible.

    """
    # Set x, y
    X = df[['x', 'y', 'color', 'dotsize', 'opacity', 'stroke', 'desc', 'x1', 'y1', 'x2', 'y2']].to_json(orient='values')
    # Return
    return X
