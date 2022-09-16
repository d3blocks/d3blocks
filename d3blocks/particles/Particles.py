"""Scatter graph."""
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time

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
        'BACKGROUND': config['background'],
        'RADIUS': config['radius'],
        'COLLISION': config['collision'],
        'FONTSIZE': config['fontsize'],
        'SPACING': config['spacing'],
        'CMAP': config['cmap'],
    }

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('particles.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))
