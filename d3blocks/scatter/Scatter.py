"""Scatter graph."""
import colourmap
import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os


# %% Preprocessing
def preprocessing(x, y, c='#69b3a2', s=5, tooltip=None, opacity=0.8, c_gradient=None, stroke='#ffffff', cmap='Set2', normalize=False):
    """Scatterplots."""
    # Combine into array
    X = np.c_[x, y]
    # Normalize data
    if normalize: X = _normalize_xy(X)
    # In case only one (s)ize is defined. Set all points to this size.
    if isinstance(s, (int, float)): s = np.repeat(s, X.shape[0])
    # In case None tooltip is defined. Set all points to this tooltip.
    if tooltip is None: tooltip = np.repeat('', X.shape[0])
    # In case only one opacity is defined. Set all points to this size.
    if isinstance(opacity, (int, float)): opacity = np.repeat(opacity, X.shape[0])
    # colors
    c, labels = set_colors(X, c, cmap, c_gradient=c_gradient)
    # In case stroke is None: use same colors as for c.
    if stroke is None:
        stroke = c
    elif isinstance(stroke, str):
        # In case only one stroke is defined. Set all points to this size.
        stroke = np.repeat(stroke, X.shape[0])

    # Make dict with properties
    dict_properties = {}
    for i in range(0, X.shape[0]):
        dict_properties[i] = {'id': labels[i], 'x': X[i][0], 'y': X[i][1], 'color': c[i], 'dotsize': s[i], 'stroke': stroke[i], 'opacity': opacity[i], 'desc': tooltip[i], 'short': labels[i]}

    # return
    return dict_properties


# %% Normalize data
def _normalize_xy(X):
    """Scatterplots."""
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    return (X - x_min) / (x_max - x_min)


# %% Setup colors
def set_colors(X, c, cmap, c_gradient=None):
    """Scatterplots."""
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
        c_hex, _ = colourmap.fromlist(c, cmap=cmap, method='matplotlib', gradient=c_gradient, scheme='hex')

    if (c_gradient is not None):
        c_hex = _density_color(X, c_hex, c)

    # Return
    return c_hex, labels


# %% Create gradient based based on the labels.
def _density_color(X, colors, labels):
    """Scatterplots."""
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
    # Compute xlim and ylim.
    spacing = 0.12
    if config['xlim']==[None, None] or len(config['xlim'])==0:
        x_spacing = (df['x'].max() - df['x'].min()) * spacing
        config['xlim'] = [df['x'].min() - x_spacing, df['x'].max() + x_spacing]
    if config['ylim']==[None, None] or len(config['ylim'])==0:
        y_spacing = (df['y'].max() - df['y'].min()) * spacing
        config['ylim'] = [df['y'].min() - y_spacing, df['y'].max() + y_spacing]

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


def write_html(X, config, overwrite=True):
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
        'MOUSEOVER': config['mouseover'],
        'MOUSEMOVE': config['mousemove'] ,
        'MOUSELEAVE': config['mouseleave'],
    }

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('scatter.html.j2')
    index_file = Path(config['filepath'])
    print('Write to path: [%s]' % index_file.absolute())
    # index_file.write_text(index_template.render(content))
    if os.path.isfile(index_file):
        if overwrite:
            print('File already exists and will be overwritten: [%s]' %(index_file))
            os.remove(index_file)
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
    X = df[['x', 'y', 'color', 'dotsize', 'opacity', 'stroke', 'desc']].to_json(orient='values')
    # Return
    return X
