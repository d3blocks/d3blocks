"""Particles block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
try:
    from .. utils import set_path
except:
    from utils import set_path


# %% Set configuration properties
def set_config(config, logger=None):
    """Set the general configuration setting."""
    config['chart'] ='Particles'
    config['title']='Particles - D3blocks'
    config['filepath']=set_path('particles.html')
    config['figsize']=[900, 200]
    config['showfig']=True
    config['overwrite']=True
    config['fontsize'] = '"' + str(180) + 'px"'
    config['radius']=3
    config['collision']=0.5
    config['spacing']=8
    config['cmap']='Turbo'
    config['background']='#000000'
    return config


def show(text, config):
    """Build and show the graph.

    Parameters
    ----------
    text : string
        String to be visualized
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    # Write to HTML
    write_html(text, config)
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
        'COLOR_BACKGROUND': config['color_background'],
        'RADIUS': config['radius'],
        'COLLISION': config['collision'],
        'FONTSIZE': config['fontsize'],
        'SPACING': config['spacing'],
        'CMAP': config['cmap'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.particles', package_path='d3js'))

    index_template = jinja_env.get_template('particles.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))
