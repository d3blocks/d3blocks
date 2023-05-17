"""Chord block.

Library     : d3blocks
Author      : E.Taskesen, O.Verver
Mail        : erdogant@gmail.com, oliver@sensibly.nl
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import colourmap
import numpy as np
import os
# from jinja2 import Environment, PackageLoader
from shutil import copyfile
try:
    from .. utils import set_path, set_labels, write_html_file
except:
    from utils import set_path, set_labels, write_html_file


# %% Set configuration properties
def set_config(config={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] ='Matrix'
    config['title'] = kwargs.get('title', 'Matrix - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', 'matrix.html'), logger)
    config['figsize'] = kwargs.get('figsize', [720, 720])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['classlabel'] = kwargs.get('classlabel', 'cluster')
    config['description'] = kwargs.get('description', '')
    config['vmax'] = kwargs.get('vmax', None)
    config['vmin'] = kwargs.get('vmin', None)
    config['stroke'] = kwargs.get('stroke', 'red')
    config['notebook'] = kwargs.get('notebook', False)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['cmap'] = kwargs.get('cmap', 'inferno')
    config['cluster_params'] = kwargs.get('cluster_params', {})
    config['scale'] = kwargs.get('scale', False)
    config['fontsize'] = kwargs.get('fontsize', 10)

    if config['description'] is None: config['description']=''
    if config['cmap'] in ['schemeCategory10', 'schemeAccent', 'schemeDark2', 'schemePaired', 'schemePastel2', 'schemePastel1', 'schemeSet1', 'schemeSet2', 'schemeSet3', 'schemeTableau10']:
        config['cmap_type']='scaleOrdinal'
    else:
        config['cmap_type']='scaleSequential'

    # return
    return config


# %% Node properties
def set_node_properties(df, **kwargs):
    """Set the node properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data containing the following columns:
        'source'
        'target'
    cmap : String, (default: 'tab20')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv','inferno'
    logger : Object, (default: None)
        Show messages on screen.

    Returns
    -------
    dict_labels : dictionary()
        Dictionary containing the label properties.

    """
    cmap = kwargs.get('cmap')
    logger = kwargs.get('logger', None)
    col_labels = kwargs.get('labels', ['source', 'target'])

    # Get unique labels
    uilabels = set_labels(df, col_labels=col_labels, logger=logger)

    # Create unique label/node colors
    colors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex', verbose=0)

    # Make dict
    dict_labels = {}
    for i, label in enumerate(uilabels):
        dict_labels[label] = {'id': i, 'label': label, 'color': colors[i]}
    # Return
    return dict_labels

def set_properties(df, config, node_properties, logger=None):
    # Checks
    if (not config['scale']) and (config['vmin'] is not None) and (config['vmax'] is not None):
        logger.info('Data is not scaled. Tip: set vmin=None and vmax=None to range colors between [min, max] of your data.')
    if config['vmin'] is None: config['vmin'] = np.min(df['weight'].values)
    if config['vmax'] is None: config['vmax'] = np.max(df['weight'].values)
    # Show debug message
    logger.debug('vmin is set to: %g' %(config['vmin']))
    logger.debug('vmax is set to: %g' %(config['vmax']))

    # Prepare the data
    json_data = get_data_ready_for_d3_matrix(df, node_properties)
    # Create the html file
    html = write_html(json_data, config, logger)
    # Return html
    return html


def write_html(json_data, config, logger=None):
    """Write html.

    Parameters
    ----------
    json_data : str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    None.

    """
    # Check path
    dirpath, filename = None, ''
    if config['filepath'] is not None:
        dirpath, filename = os.path.split(config['filepath'])

    # Set fontsize for x-axis, y-axis
    fontsize_x = config['fontsize']
    fontsize_y = config['fontsize']

    # Get path to files
    d3_library = os.path.abspath(os.path.join(config['curpath'], 'matrix/d3js/d3.v4.js'))
    d3_chromatic = os.path.abspath(os.path.join(config['curpath'], 'matrix/d3js/d3.scale.chromatic.v1.min.js'))
    # with open(d3_library, 'r', encoding="utf8", errors='ignore') as file: d3_library = file.read()
    # with open(d3_chromatic, 'r', encoding="utf8", errors='ignore') as file: d3_chromatic = file.read()
    # Check path
    copyfile(d3_library, os.path.join(dirpath, os.path.basename(d3_library)))
    copyfile(d3_chromatic, os.path.join(dirpath, os.path.basename(d3_chromatic)))

    # Import in the file
    d3_script = os.path.abspath(os.path.join(config['curpath'], 'matrix/d3js/matrix.html.j2'))
    with open(d3_script, 'r', encoding="utf8", errors='ignore') as file: html = file.read()

    # Read the d3 html with script file
    html = html.replace('$DESCRIPTION$', str(config['description']))
    html = html.replace('$TITLE$', str(config['title']))
    html = html.replace('$WIDTH$', str(config['figsize'][0]))
    html = html.replace('$HEIGHT$', str(config['figsize'][1]))
    html = html.replace('$VMIN$', str(config['vmin']))
    html = html.replace('$VMAX$', str(config['vmax']))
    html = html.replace('$FONTSIZE_X$', str(fontsize_x))
    html = html.replace('$FONTSIZE_Y$', str(fontsize_y))
    html = html.replace('$STROKE$', str(config['stroke']))
    html = html.replace('$CMAP$', str(config['cmap']))
    html = html.replace('$CMAP_TYPE$', str(config['cmap_type']))
    html = html.replace('$DATA_PATH$', filename)
    html = html.replace('$SUPPORT$', config['support'])
    html = html.replace('$DATA_COMES_HERE$', json_data)
    # html = html.replace('src="d3.v4.js"', d3_library)
    # html = html.replace('src="d3.scale.chromatic.v1.min.js"', d3_chromatic)

    # content = {
    #     'DESCRIPTION': str(config['description']),
    #     'TITLE': str(config['title']),
    #     'WIDTH': str(config['figsize'][0]),
    #     'HEIGHT': str(config['figsize'][0]),
    #     'VMIN': str(config['vmin']),
    #     'VMAX': str(config['vmax']),
    #     'FONTSIZE_X': str(fontsize_x),
    #     'FONTSIZE_Y': str(fontsize_y),
    #     'STROKE': str(config['stroke']),
    #     'CMAP': str(config['cmap']),
    #     'CMAP_TYPE': str(config['cmap_type']),
    #     'DATA_COMES_HERE': json_data,
    # }

    # try:
    #     jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    # except:
    #     jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.matrix', package_path='d3js'))

    # index_template = jinja_env.get_template('matrix.html.j2')
    # # Generate html content
    # html = index_template.render(content)

    # Write to html
    write_html_file(config, html, logger)
    return html



def get_data_ready_for_d3_matrix(df, node_properties):
    """
    Embed the Data in the HTML. Note that the embedding is an important stap te prevent security issues by the browsers.
    Most (if not all) browser do not accept to read a file using d3.csv or so. It then requires security-by-passes, but thats not the way to go.
    An alternative is use local-host and CORS but then the approach is not user-friendly coz setting up this, is not so straightforward.
    It leaves us by embedding the data in the HTML. Thats what we are going to do here.

    Parameters
    ----------
    df : pd.DataFrame()
        Input data.
    labels : dict
        Dictionary containing hex colorlabels for the classes.
        The labels are derived using the function: labels = d3blocks.set_label_properties()

    Returns
    -------
    json_data : str.
        Converted data into a string that is d3 compatible.

    """
    # Convert into adj into vector
    df = df.rename(columns={'source': 'variable', 'target': 'group', 'weight': 'value'})
    json_data = ''

    for i in range(0, df.shape[0]):
        newline = '{group : "' + str(df['group'].iloc[i]) + '", variable : "' + str(df['variable'].iloc[i]) + '", value : "' + str(df['value'].iloc[i]) +'"},'
        newline = newline + '\n'
        json_data = json_data + newline

    # Read the data
    # var data =
    # 	[
    # 		{"group":"A", "variable":"v1", "value":"3"},
    # 		{"group":"A", "variable":"v2", "value":"5"},
    # 		{"group":"B", "variable":"v1", "value":"10"},
    # 		{"group":"B", "variable":"v2", "value":"10"}
    # 	]
    return json_data
